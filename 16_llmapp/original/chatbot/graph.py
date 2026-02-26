"""
graph.py

LangGraphを使って、Web検索、RAG、ルールベースのリスクスコアリングをまとめたチャット処理を構築
"""

import os
from typing import Annotated, Optional
from typing_extensions import TypedDict

import tiktoken
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from chatbot.config import (
    MODEL_NAME,
    EMBEDDING_MODEL,
    TAVILY_MAX_RESULTS,
    DATA_TEXT_DIR,
    PERSIST_DIR,
)
from chatbot.risk_score import compute_wind_risk

load_dotenv(".env")
os.environ["OPENAI_API_KEY"] = os.environ.get("API_KEY", "")

memory = MemorySaver()

graph = None


class State(TypedDict):
    """
    入力値:
      - messages: LangGraphのメッセージ配列

    出力値:
      - messages: 応答追加後のメッセージ配列
    """
    messages: Annotated[list, add_messages]


def create_index(persist_directory: str, embedding_model: OpenAIEmbeddings) -> Chroma:
    """
    テキストデータからChromaインデックスを作成する。

    入力値:
      - persist_directory: インデックス保存先ディレクトリ
      - embedding_model: テキストをベクトル化するモデル

    出力値:
      - Chroma: 作成したベクタDB
    """
    loader = DirectoryLoader(
        DATA_TEXT_DIR,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()

    # モデルに合わせたtokenizerを使う
    encoding_name = tiktoken.encoding_for_model(MODEL_NAME).name
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        encoding_name=encoding_name,
        chunk_size=800,
        chunk_overlap=100,
    )
    texts = splitter.split_documents(documents)

    db = Chroma.from_documents(texts, embedding_model, persist_directory=persist_directory)
    return db


def define_tools():
    """
    LLMに渡すツール群を定義する。

    出力値:
      - tools(list): ToolNodeへ渡せるツール配列
    """
    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # 既存DBがあれば再利用。壊れている場合は作り直す。
    if os.path.exists(PERSIST_DIR):
        try:
            db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_model)
        except Exception:
            db = create_index(PERSIST_DIR, embedding_model)
    else:
        db = create_index(PERSIST_DIR, embedding_model)

    retriever = db.as_retriever(search_kwargs={"k": 3})
    rag_tool = create_retriever_tool(
        retriever,
        "retrieve_bike_wind_manual",
        "Search and return bike wind safety manual snippets (tie-down, cover risk, parking tips).",
    )

    # Web search
    tavily_tool = TavilySearchResults(max_results=TAVILY_MAX_RESULTS)

    # Risk scoring
    @tool("compute_wind_risk")
    def compute_wind_risk_tool(
            prefecture: str,
            parking_type: str,
            has_cover: bool,
            has_bike_fixing_gear: bool,
            web_summary: Optional[str] = None,
    ) -> str:
        """
        ルールベースの風害リスク算出をツール化する。

        入力値:
          - prefecture: 都道府県名
          - parking_type: 駐車環境
          - has_cover: カバー有無
          - has_bike_fixing_gear: バイクの固定具 有無
          - web_summary: Web検索要約

        出力値:
          - JSON風文字列
        """
        result = compute_wind_risk(
            prefecture=prefecture,
            parking_type=parking_type,
            has_cover=has_cover,
            has_bike_fixing_gear=has_bike_fixing_gear,
            web_summary=web_summary,
        )
        return (
            "{"
            f"\"score\": {result.score}, "
            f"\"level\": \"{result.level}\", "
            f"\"reasons\": {result.reasons}"
            "}"
        )

    return [rag_tool, tavily_tool, compute_wind_risk_tool]


def build_graph(model_name: str, memory_saver: MemorySaver):
    """
    LangGraphのgraphを組み立てる。

    入力値:
      - model_name: OpenAIチャットモデル名
      - memory_saver: 会話履歴保存用

    出力値:
      - compiled_graph: graph.invoke 可能な実体
    """
    tools = define_tools()

    # 課題ではtemperature低めにして挙動を安定化
    llm = ChatOpenAI(model_name=model_name, temperature=0.2)
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = (
        "あなたはバイクの転倒防止チェックを行うアシスタントです。\n"
        "目的: ユーザーの入力（都道府県、駐車環境、カバー、固定具）と、必要なら最新情報を踏まえて、"
        "転倒リスクを評価し対策を提示してください。\n"
        "\n"
        "ルール:\n"
        "- 必要に応じてWeb検索ツールを使い『{都道府県} 強風 注意報 予報』などを調べる。\n"
        "- 必要に応じてRAGツールでローカルマニュアルから根拠を1つ引用する。\n"
        "- 必ず compute_wind_risk ツールを呼び、スコア(0-100)と判定(低/中/高)を出す。\n"
        "- 最終回答は次のフォーマットで出力する。\n"
        "\n"
        "【判定】低/中/高\n"
        "【リスクスコア】0-100\n"
        "【理由】\n"
        "- ...\n"
        "- ...\n"
        "- ...\n"
        "【今すぐやること】\n"
        "1) ...\n"
        "2) ...\n"
        "3) ...\n"
        "【根拠】\n"
        "- Web要約: ...\n"
        "- マニュアル: ...（引用）\n"
    )

    def chatbot_node(state: State):
        """
        1ターン分のLLM応答生成

        入力値:
          - state: messagesを含む状態

        出力値:
          - {"messages": [AIMessage]} を返し、LangGraphが履歴に積む
        """
        messages = [("system", system_prompt)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}

    builder = StateGraph(State)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("chatbot", chatbot_node)

    # chatbotがtool呼び出しを選んだらtoolsへ、そうでなければ終了
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    builder.set_entry_point("chatbot")

    return builder.compile(checkpointer=memory_saver)


def stream_graph_updates(graph_obj, user_message: str, thread_id: str) -> str:
    """
    graphにユーザー入力を与えて最終応答テキストを取り出す。

    入力値:
      - graph_obj: build_graphで作成したgraph
      - user_message: ユーザー発話
      - thread_id: セッション識別子

    出力値:
      - bot_message(str): 最終AI応答テキスト
    """
    response = graph_obj.invoke(
        {"messages": [("user", user_message)]},
        {"configurable": {"thread_id": thread_id}},
        stream_mode="values",
    )
    return response["messages"][-1].content


def get_bot_response(user_message: str, memory_saver: MemorySaver, thread_id: str) -> str:
    """
    graphを遅延生成しつつ、応答を返す。

    入力値:
      - user_message: ユーザー入力
      - memory_saver: 会話履歴
      - thread_id: セッションID

    出力値:
      - AI応答テキスト
    """
    global graph
    if graph is None:
        graph = build_graph(MODEL_NAME, memory_saver)
    return stream_graph_updates(graph, user_message, thread_id)


def get_messages_list(memory_saver: MemorySaver, thread_id: str):
    """
    セッションの会話履歴を画面表示用に整形する。

    入力値:
      - memory_saver: 会話履歴
      - thread_id: セッションID

    出力値:
      - list[dict]: [{"class": "...", "text": "..."}] 形式
    """
    messages = []
    saved = memory_saver.get({"configurable": {"thread_id": thread_id}})
    if not saved:
        return messages

    # MemorySaverに保存されているmessagesを取り出す
    memories = saved["channel_values"]["messages"]
    for m in memories:
        if isinstance(m, HumanMessage):
            messages.append({"class": "user-message", "text": m.content.replace("\n", "<br>")})
        elif isinstance(m, AIMessage) and m.content != "":
            messages.append({"class": "bot-message", "text": m.content.replace("\n", "<br>")})

    return messages