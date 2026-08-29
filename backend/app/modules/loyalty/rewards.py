def calculate_loyalty_points(basket_total: float, tier: str = "SILVER") -> dict:
    multipliers = {"SILVER": 1.0, "GOLD": 1.5, "PLATINUM": 2.0}
    mult = multipliers.get(tier.upper(), 1.0)
    earned_points = int(basket_total * mult)
    cashback_value = round(earned_points * 0.05, 2)
    return {"earned_points": earned_points, "cashback_value": cashback_value}
