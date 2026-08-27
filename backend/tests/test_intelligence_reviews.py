"""Smart Substitutions, Grocery Replenishment Planner, and Verified Reviews Tests."""
from datetime import date, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_substitutions_planner_and_reviews_flow(client: AsyncClient):
    # 1. Register Users
    admin_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "admin_intel@freshcart.com", "password": "Password123!", "full_name": "Admin Lead", "role": "ADMIN"},
    )
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    cust_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "planner_user@freshcart.com", "password": "Password123!", "full_name": "Priya Sharma", "role": "CUSTOMER"},
    )
    cust_token = cust_res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Create Category & Products for Substitution (Butter A & Butter B)
    cat_res = await client.post("/api/v1/categories", json={"name": "Dairy & Spreads"}, headers=admin_headers)
    cat_id = cat_res.json()["id"]

    # Product A: Amul Salted Butter 500g (₹275)
    p_a = await client.post(
        "/api/v1/products",
        json={
            "sku": "BUTTER-AMUL-500G",
            "name": "Amul Butter Pasteurised 500g",
            "brand": "Amul",
            "category_id": cat_id,
            "unit": "pack",
            "base_price": 285.0,
            "sale_price": 275.0,
        },
        headers=admin_headers,
    )
    pa_id = p_a.json()["id"]

    # Product B: Mother Dairy Butter 500g (₹270)
    p_b = await client.post(
        "/api/v1/products",
        json={
            "sku": "BUTTER-MD-500G",
            "name": "Mother Dairy Table Butter 500g",
            "brand": "Mother Dairy",
            "category_id": cat_id,
            "unit": "pack",
            "base_price": 280.0,
            "sale_price": 270.0,
        },
        headers=admin_headers,
    )
    pb_id = p_b.json()["id"]

    # 3. Test Smart Substitutions Engine
    sub_res = await client.get(f"/api/v1/substitutions/suggest/{pa_id}")
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert len(sub_data["suggestions"]) >= 1
    assert sub_data["suggestions"][0]["product"]["id"] == pb_id
    assert sub_data["suggestions"][0]["price_delta"] == -5.0

    # 4. Smart Weekly Grocery Planner
    next_week = date.today() + timedelta(days=7)
    plan_res = await client.post(
        "/api/v1/recommendations/smart-planner",
        json={
            "plan_name": "Sharma Household Weekly Essentials",
            "frequency_days": 7,
            "next_replenishment_date": next_week.isoformat(),
            "items": [
                {"product_id": pa_id, "quantity": 2.0, "aisle_category": "Dairy"},
                {"product_id": pb_id, "quantity": 1.0, "aisle_category": "Spreads"},
            ],
        },
        headers=cust_headers,
    )
    assert plan_res.status_code == 201
    plan_data = plan_res.json()
    plan_id = plan_data["id"]
    assert len(plan_data["items"]) == 2

    # Auto-generate Cart from Smart Plan
    gen_cart = await client.post(f"/api/v1/recommendations/smart-planner/{plan_id}/generate-cart", headers=cust_headers)
    assert gen_cart.status_code == 200
    cart_dto = gen_cart.json()
    assert cart_dto["total_items"] == 2
    # Subtotal: (275 * 2) + (270 * 1) = 820
    assert cart_dto["subtotal"] == 820.0

    # 5. Verified Product Reviews & Rating Recalculation
    review_res = await client.post(
        f"/api/v1/reviews/product/{pa_id}",
        json={
            "rating": 5,
            "title": "Classic taste and top quality!",
            "comment": "Always fresh, best taste with toast and parathas.",
        },
        headers=cust_headers,
    )
    assert review_res.status_code == 201
    rev_id = review_res.json()["id"]

    # Check product rating average updated
    prod_check = (await client.get(f"/api/v1/products/{pa_id}")).json()
    assert prod_check["rating_average"] == 5.0
    assert prod_check["rating_count"] == 1

    # Helpful Upvote
    upvote_res = await client.post(f"/api/v1/reviews/{rev_id}/vote-helpful")
    assert upvote_res.status_code == 200
    assert upvote_res.json()["helpful_votes"] == 1
