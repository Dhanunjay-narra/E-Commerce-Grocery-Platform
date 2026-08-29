from datetime import datetime, timezone, timedelta

def calculate_dynamic_expiry_discount(original_price: float, expiry_date: datetime) -> dict:
    now = datetime.now(timezone.utc)
    days_left = (expiry_date - now).days
    if days_left <= 1:
        discount_pct = 50.0
    elif days_left <= 3:
        discount_pct = 30.0
    elif days_left <= 5:
        discount_pct = 15.0
    else:
        discount_pct = 0.0
        
    discounted_price = round(original_price * (1.0 - (discount_pct / 100.0)), 2)
    return {"original_price": original_price, "discount_pct": discount_pct, "discounted_price": discounted_price, "days_left": days_left}
