"""Tests for Categories, Master Product Catalog, Variable Weight Pricing, and Search."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_category_and_product_catalog(client: AsyncClient):
    # 1. Register Admin User
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@freshcart.com",
            "password": "AdminPassword123!",
            "full_name": "Admin Dhanunjay",
            "role": "ADMIN",
        },
    )
    assert reg_res.status_code == 201
    admin_token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create 3-Tier Category Hierarchy
    # Level 0: Department (Fresh Produce)
    dept_res = await client.post(
        "/api/v1/categories",
        json={"name": "Fresh Produce", "icon_name": "Apple", "is_featured": True},
        headers=headers,
    )
    assert dept_res.status_code == 201
    dept_id = dept_res.json()["id"]

    # Level 1: Category (Vegetables)
    cat_res = await client.post(
        "/api/v1/categories",
        json={"name": "Vegetables", "parent_id": dept_id, "is_featured": True},
        headers=headers,
    )
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["id"]
    assert cat_res.json()["level"] == 1

    # Level 2: Subcategory (Daily Vegetables)
    subcat_res = await client.post(
        "/api/v1/categories",
        json={"name": "Daily Vegetables", "parent_id": cat_id},
        headers=headers,
    )
    assert subcat_res.status_code == 201
    subcat_id = subcat_res.json()["id"]
    assert subcat_res.json()["level"] == 2

    # Verify Tree Structure
    tree_res = await client.get("/api/v1/categories/tree")
    assert tree_res.status_code == 200
    tree = tree_res.json()
    assert len(tree) >= 1
    assert tree[0]["name"] == "Fresh Produce"
    assert len(tree[0]["subcategories"]) >= 1

    # 3. Create Variable-Weight Product (Farm Fresh Organic Tomatoes)
    prod_payload = {
        "sku": "VEG-TOM-001",
        "barcode": "8901234567890",
        "name": "Farm Fresh Organic Tomatoes",
        "brand": "Organic Valley",
        "description": "Vine-ripened organic red tomatoes, pesticide free.",
        "category_id": subcat_id,
        "unit": "kg",
        "base_price": 60.0,
        "sale_price": 50.0,
        "is_variable_weight": True,
        "weight_increment": 0.5,
        "weight_tolerance_pct": 15.0,
        "is_organic": True,
        "is_vegetarian": True,
        "is_vegan": True,
        "storage_instructions": "Store in a cool dry place (12-15°C)",
        "shelf_life_days": 7,
    }
    prod_res = await client.post("/api/v1/products", json=prod_payload, headers=headers)
    assert prod_res.status_code == 201
    prod_data = prod_res.json()
    prod_id = prod_data["id"]
    assert prod_data["is_variable_weight"] is True
    assert prod_data["sku"] == "VEG-TOM-001"

    # 4. Test Variable Weight Calculation
    # Ordered 1.0 kg, actual scale weight picked is 1.08 kg
    calc_res = await client.post(
        f"/api/v1/products/{prod_id}/calc-variable-price",
        json={"requested_qty": 1.0, "actual_picked_qty": 1.08},
    )
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["estimated_price"] == 50.0  # 1.0 kg * 50.0
    assert calc_data["final_reconciled_price"] == 54.0  # 1.08 kg * 50.0 = 54.0
    assert calc_data["price_delta"] == 4.0
    assert calc_data["is_within_tolerance"] is True

    # 5. Search with Typo Tolerance ("tomatos")
    search_res = await client.get("/api/v1/search?q=tomatos")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 1
    assert search_data["items"][0]["name"] == "Farm Fresh Organic Tomatoes"
    assert "categories" in search_data["facets"]

    # 6. Autocomplete Keystroke Suggestions
    sugg_res = await client.get("/api/v1/search/suggestions?q=toma")
    assert sugg_res.status_code == 200
    suggs = sugg_res.json()
    assert len(suggs) >= 1
    assert any("Tomatoes" in s["text"] for s in suggs)
