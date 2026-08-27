"""User profile, address, dietary preference, and household tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_addresses_and_household(client: AsyncClient):
    # 1. Register user
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "household_user@example.com",
            "password": "Password123!",
            "full_name": "Household Lead",
            "role": "CUSTOMER",
        },
    )
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add Address
    addr_payload = {
        "label": "Home",
        "recipient_name": "Household Lead",
        "recipient_phone": "+919876543210",
        "street_address": "Flat 402, Green Valley Apartments",
        "city": "Hyderabad",
        "state": "Telangana",
        "postal_code": "500081",
        "country": "India",
        "is_default": True,
    }
    addr_res = await client.post("/api/v1/users/me/addresses", json=addr_payload, headers=headers)
    assert addr_res.status_code == 201
    addr_data = addr_res.json()
    assert addr_data["city"] == "Hyderabad"
    assert addr_data["is_default"] is True

    # 3. Dietary preferences
    diet_payload = {
        "is_vegetarian": True,
        "is_organic_only": True,
        "allergies": "peanuts",
    }
    diet_res = await client.put("/api/v1/users/me/dietary-preferences", json=diet_payload, headers=headers)
    assert diet_res.status_code == 200
    assert diet_res.json()["is_vegetarian"] is True

    # 4. Household creation
    hh_res = await client.post("/api/v1/users/me/household", json={"name": "The Green Family"}, headers=headers)
    assert hh_res.status_code == 201
    hh_data = hh_res.json()
    assert hh_data["name"] == "The Green Family"
    assert len(hh_data["members"]) == 1

    # 5. Add shopping list item
    item_res = await client.post(
        "/api/v1/users/me/household/items",
        json={"custom_name": "Organic Almond Milk", "quantity": 2.0, "unit": "bottles"},
        headers=headers,
    )
    assert item_res.status_code == 201
    assert item_res.json()["custom_name"] == "Organic Almond Milk"
