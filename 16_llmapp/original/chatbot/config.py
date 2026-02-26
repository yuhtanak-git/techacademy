"""
config.py

アプリ全体の設定値
"""
import os

# LLM / Embeddings
MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Web検索
TAVILY_MAX_RESULTS = 3

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_TEXT_DIR = os.path.join(BASE_DIR, "data", "text")
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")

# UIプルダウン用
PREFECTURES = [
    "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
    "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
    "新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県",
    "三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
    "鳥取県","島根県","岡山県","広島県","山口県",
    "徳島県","香川県","愛媛県","高知県",
    "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県",
    "沖縄県",
]

# 駐車環境
PARKING_TYPES = [
    ("outdoor", "屋外（吹きさらし）"),
    ("roof", "屋根あり（半屋外）"),
    ("indoor", "屋内（ほぼ影響なし）"),
]