"""
app.py

Flaskアプリ本体
"""

import sys
import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, make_response, session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.graph import get_bot_response, get_messages_list, memory
from chatbot.config import PREFECTURES, PARKING_TYPES

load_dotenv(".env")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key")


def build_user_message(form) -> str:
    """
    画面入力をLLM向けの文章に整形する。

    入力値:
      - form: Flaskのリクエストフォーム

    出力値:
      - user_message(str): LLMに渡すテキスト
    """
    prefecture = form.get("prefecture", "")
    parking_type = form.get("parking_type", "")

    has_cover = form.get("has_cover") == "on"
    has_bike_fixing_gear = form.get("has_bike_fixing_gear") == "on"

    free_text = (form.get("free_text") or "").strip()

    lines = []
    lines.append(f"都道府県: {prefecture}")
    lines.append(f"駐車環境: {parking_type}")
    lines.append(f"カバー: {'あり' if has_cover else 'なし'}")
    lines.append(f"バイクの固定具: {'あり' if has_bike_fixing_gear else 'なし'}")

    if free_text:
        lines.append(f"追加メモ: {free_text}")

    # LLMがやるべきこと（評価→対策）を明示
    lines.append("依頼: 風害による転倒リスクを評価し、対策を提案して。必要ならWeb検索とマニュアル検索を使って。")
    return "\n".join(lines)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    画面表示・入力受け取りのメイン。

    入力値:
      - GET: 初期表示
      - POST: 入力を受け取り、LLM応答を生成して再表示

    出力値:
      - HTMLレスポンス
    """
    # セッションごとにthread_idを持つ（会話履歴の切り分け用）
    if "thread_id" not in session:
        session["thread_id"] = str(uuid.uuid4())

    if request.method == "GET":
        return make_response(render_template(
            "index.html",
            messages=[],
            prefectures=PREFECTURES,
            parking_types=PARKING_TYPES,
        ))

    user_message = build_user_message(request.form)

    # 応答生成（memoryに保存される）
    get_bot_response(user_message, memory, session["thread_id"])

    # 表示用に履歴を取得
    messages = get_messages_list(memory, session["thread_id"])

    return make_response(render_template(
        "index.html",
        messages=messages,
        prefectures=PREFECTURES,
        parking_types=PARKING_TYPES,
    ))


@app.route("/clear", methods=["POST"])
def clear():
    """
    履歴消去。

    入力値:
      - POSTのみ

    出力値:
      - 初期状態のHTML
    """
    session.pop("thread_id", None)

    # MemorySaverは共有ストレージのため、本来はthread_id単位消去が理想。
    # 課題提出規模では簡単に全消去。
    memory.storage.clear()

    return make_response(render_template(
        "index.html",
        messages=[],
        prefectures=PREFECTURES,
        parking_types=PARKING_TYPES,
    ))


if __name__ == "__main__":
    # デバッグ起動
    app.run(debug=True)