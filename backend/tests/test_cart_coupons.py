"""Shopping Cart, Multi-Vendor Partitions, Coupons, and Wishlist Tests."""
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cart_coupons_and_wishlist_flow(client: AsyncClient):
    # 1. Register Customer & Admin
    admin_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "admin_cart@freshcart.com", "password": "Password123!", "full_name": "Admin Lead", "role": "ADMIN"},
    )
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    cust_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "shopper_cart@freshcart.com", "password": "Password123!", "full_name": "Active Shopper", "role": "CUSTOMER"},
    )
    cust_token = cust_res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Create Category & Products
    cat_res = await client.post("/api/v1/categories", json={"name": "Pantry Staples"}, headers=admin_headers)
    cat_id = cat_res.json()["id"]

    # Product 1: Basmati Rice 5kg (₹550)
    p1_res = await client.post(
        "/api/v1/products",
        json={
            "sku": "RICE-BAS-5KG",
            "name": "Royal Basmati Rice 5kg",
            "brand": "Daawat",
            "category_id": cat_id,
            "unit": "kg",
            "base_price": 600.0,
            "sale_price": 550.0,
        },
        headers=admin_headers,
    )
    p1_id = p1_res.json()["id"]

    # Product 2: Cold Pressed Groundnut Oil 1L (₹220)
    p2_res = await client.post(
        "/api/v1/products",
        json={
            "sku": "OIL-GNUT-1L",
            "name": "Cold Pressed Groundnut Oil 1L",
            "brand": "Puvi",
            "category_id": cat_id,
            "unit": "L",
            "base_price": 250.0,
            "sale_price": 220.0,
        },
        headers=admin_headers,
    )
    p2_id = p2_res.json()["id"]

    # 3. Create Coupon: WELCOME100 (₹100 off on min order ₹500)
    exp = datetime.now(timezone.utc) + timedelta(days=30)
    c_res = await client.post(
        "/api/v1/coupons",
        json={
            "code": "WELCOME100",
            "description": "Flat ₹100 off on first grocery orders above ₹500",
            "discount_type": "FIXED_AMOUNT",
            "discount_value": 100.0,
            "min_order_value": 500.0,
            "expires_at": exp.isoformat(),
        },
        headers=admin_headers,
    )
    assert c_res.status_code == 201

    # 4. Add items to Cart
    add1 = await client.post(
        "/api/v1/cart/items",
        json={"product_id": p1_id, "quantity": 1.0},
        headers=cust_headers,
    )
    assert add1.status_code == 201
    cart_data = add1.json()
    assert cart_data["subtotal"] == 550.0

    # 5. Apply Coupon
    apply_res = await client.post(
        "/api/v1/cart/apply-coupon",
        json={"coupon_code": "WELCOME100"},
        headers=cust_headers,
    )
    assert apply_res.status_code == 200
    cart_after_coupon = apply_res.json()
    assert cart_after_coupon["coupon_code"] == "WELCOME100"
    assert cart_after_coupon["discount_amount"] == 100.0
    assert cart_after_coupon["grand_total"] == 450.0  # 550 - 100

    # 6. Wishlist Management: Create Wishlist & Move to Cart
    wl_res = await client.post(
        "/api/v1/wishlists",
        json={"name": "Monthly Cooking Essentials"},
        headers=cust_headers,
    )
    assert wl_res.status_code == 201
    wl_id = wl_res.json()["id"]

    # Add Oil to Wishlist
    add_wl = await client.post(
        f"/api/v1/wishlists/{wl_id}/items",
        json={"product_id": p2_id, "desired_qty": 2.0},
        headers=cust_headers,
    )
    assert add_wl.status_code == 200
    assert len(add_wl.json()["items"]) == 1

    # Transfer Wishlist to Cart
    move_res = await client.post(f"/api/v1/wishlists/{wl_id}/move-to-cart", headers=cust_headers)
    assert move_res.status_code == 200
    assert move_res.json()["items_moved_count"] == 1

    # Verify Cart now has both products
    final_cart = (await client.get("/api/v1/cart", headers=cust_headers)).json()
    assert final_cart["total_items"] == 2
    # Subtotal: 550 + (220 * 2) = 990
    assert final_cart["subtotal"] == 990.0
    # Grand total: 990 - 100 = 890
    assert final_cart["grand_total"] == 890.0
