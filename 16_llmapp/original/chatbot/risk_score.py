"""
risk_score.py

風害による転倒リスクのスコアリング
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RiskResult:
    score: int # リスクのスコア（0-100の整数）
    level: str # リスクレベル（低、中、高）
    reasons: List[str] # リスク理由


def _clamp(value: int, min_value: int = 0, max_value: int = 100) -> int:
    """
    数値を指定範囲に収める。

    Args:
        value: 対象の数値
        min_value: 下限値
        max_value: 上限値

    Returns:
        int: 下限〜上限の範囲内に補正された数値
    """
    return max(min_value, min(max_value, value))


def compute_wind_risk(
        prefecture: str,
        parking_type: str,
        has_cover: bool,
        has_bike_fixing_gear: bool,
        web_summary: Optional[str] = None,
) -> RiskResult:
    """
    風害転倒リスクをルールベースで算出する。

    入力値:
      - prefecture: 都道府県名
      - parking_type: outdoor、roof、indoor"
      - has_cover: カバーの有無
      - has_bike_fixing_gear: バイクの固定具の有無
      - web_summary: Web検索結果の要約文字列

    出力値:
      - RiskResult(score, level, reasons)
    """
    score = 0
    reasons: List[str] = []

    # 駐車環境による基礎加点
    if parking_type == "outdoor":
        score += 25
        reasons.append("屋外駐車は突風の影響を受けやすい")
    elif parking_type == "roof":
        score += 15
        reasons.append("屋根ありでも横風・巻き込み風の影響が残る")
    elif parking_type == "indoor":
        score += 3
        reasons.append("屋内は風の影響が小さい")
    else:
        # 想定外値は安全側で処理する
        score += 10
        reasons.append("駐車環境が不明なため安全側に評価")

    # 固定具の有無
    if not has_bike_fixing_gear:
        score += 15
        reasons.append("固定具が無いと転倒しやすい")
    else:
        score -= 10
        reasons.append("固定具があるため転倒リスクが下がる")

    # カバー有無
    if has_cover:
        score += 10
        reasons.append("カバーは風を受けて転倒リスクが上がる場合がある")

    # Web要約から危険ワード検知
    text = (web_summary or "").lower()

    if any(k.lower() in text for k in ["暴風警報", "暴風", "storm warning"]):
        score += 45
        reasons.append("暴風相当の情報が見つかった")

    if any(k.lower() in text for k in ["強風注意報", "強風", "gust", "gale"]):
        score += 25
        reasons.append("強風相当の情報が見つかった")

    if any(k.lower() in text for k in ["注意報", "警報"]):
        score += 10
        reasons.append("注意報・警報に関連する記載がある")

    score = _clamp(score)

    # 判定レベル
    if score >= 70:
        level = "高"
    elif score >= 40:
        level = "中"
    else:
        level = "低"

    # 理由は多すぎると読みにくいので最大4つに制限
    reasons = reasons[:4]

    return RiskResult(score=score, level=level, reasons=reasons)