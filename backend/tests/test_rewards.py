from app.modules.loyalty.rewards import calculate_loyalty_points

def test_loyalty_points_calculation():
    res = calculate_loyalty_points(100.0, "PLATINUM")
    assert res["earned_points"] == 200
    assert res["cashback_value"] == 10.0
