from chatbot.risk_score import compute_wind_risk

def test_high_risk_outdoor_no_fixing_gear_with_warning():
    r = compute_wind_risk(
        prefecture="群馬県",
        parking_type="outdoor",
        has_cover=True,
        has_bike_fixing_gear=False,
        web_summary="群馬県 強風注意報 が発表されています",
    )
    assert r.score >= 70
    assert r.level == "高"

def test_low_risk_indoor_fixing_gear_no_warning():
    r = compute_wind_risk(
        prefecture="東京都",
        parking_type="indoor",
        has_cover=False,
        has_bike_fixing_gear=True,
        web_summary="特に注意報は見当たりません",
    )
    assert r.score < 40
    assert r.level == "低"