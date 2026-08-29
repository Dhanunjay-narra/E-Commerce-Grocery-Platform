from datetime import datetime, timezone, timedelta
from app.modules.products.perishable import calculate_dynamic_expiry_discount

def test_perishable_expiry_markdown():
    exp = datetime.now(timezone.utc) + timedelta(days=2)
    res = calculate_dynamic_expiry_discount(10.0, exp)
    assert res["discount_pct"] == 30.0
    assert res["discounted_price"] == 7.0
