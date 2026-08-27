"""FEFO Inventory Management, Batch Allocation, and Vendor Marketplace Tests."""
from datetime import datetime, timezone, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_vendor_and_fefo_inventory_lifecycle(client: AsyncClient):
    # 1. Register Admin and Vendor Owner
    admin_reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "admin_fefo@freshcart.com", "password": "Password123!", "full_name": "Admin Lead", "role": "ADMIN"},
    )
    admin_token = admin_reg.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    vendor_reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "vendor_owner@organicfarms.com", "password": "Password123!", "full_name": "Farmer John", "role": "CUSTOMER"},
    )
    vendor_token = vendor_reg.json()["access_token"]
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}

    # 2. Register Vendor Business
    vendor_payload = {
        "business_name": "Organic Greens Farm",
        "email": "contact@organicfarms.com",
        "phone": "+919876500111",
        "tax_id": "GSTIN36AAAAA0000A1Z5",
        "store": {
            "store_name": "Organic Greens Dark Store 1",
            "address_street": "Plot 12, HITEC City",
            "city": "Hyderabad",
            "state": "Telangana",
            "postal_code": "500081",
            "latitude": 17.4435,
            "longitude": 78.3772,
            "delivery_radius_km": 10.0,
        },
    }
    v_res = await client.post("/api/v1/vendors/register", json=vendor_payload, headers=vendor_headers)
    assert v_res.status_code == 201
    vendor_data = v_res.json()
    vendor_id = vendor_data["id"]
    assert vendor_data["kyc_status"] == "PENDING"

    # 3. Admin Approves KYC
    kyc_res = await client.patch(
        f"/api/v1/vendors/{vendor_id}/kyc",
        json={"kyc_status": "APPROVED", "kyc_notes": "Verified business documents", "commission_rate": 7.5},
        headers=admin_headers,
    )
    assert kyc_res.status_code == 200
    assert kyc_res.json()["kyc_status"] == "APPROVED"
    assert kyc_res.json()["commission_rate"] == 7.5

    # 4. Create Category & Product (Fresh Milk 1L)
    cat_res = await client.post(
        "/api/v1/categories",
        json={"name": "Dairy & Milk", "is_featured": True},
        headers=admin_headers,
    )
    cat_id = cat_res.json()["id"]

    prod_res = await client.post(
        "/api/v1/products",
        json={
            "sku": "DAIRY-MILK-1L",
            "name": "Fresh Pasteurized Organic Milk 1L",
            "brand": "Organic Greens Farm",
            "category_id": cat_id,
            "unit": "L",
            "base_price": 75.0,
            "sale_price": 68.0,
            "is_organic": True,
            "is_vegetarian": True,
            "shelf_life_days": 4,
        },
        headers=admin_headers,
    )
    prod_id = prod_res.json()["id"]

    # 5. Create Warehouse
    wh_res = await client.post(
        "/api/v1/inventory/warehouses",
        json={
            "name": "Hyderabad Central Hub",
            "code": "HYD-HUB-01",
            "type": "DARK_STORE",
            "address": "Gachibowli Main Rd",
            "city": "Hyderabad",
            "latitude": 17.4400,
            "longitude": 78.3489,
        },
        headers=admin_headers,
    )
    assert wh_res.status_code == 201
    wh_id = wh_res.json()["id"]

    # 6. Create Two Batches with Different Expiries (FEFO Test Setup)
    # Batch 1: Expiring in 2 days (Quantity: 10)
    expiry_soon = datetime.now(timezone.utc) + timedelta(days=2)
    b1_res = await client.post(
        "/api/v1/inventory/batches",
        json={
            "batch_number": "LOT-MILK-SOON-01",
            "product_id": prod_id,
            "vendor_id": vendor_id,
            "warehouse_id": wh_id,
            "expiry_date": expiry_soon.isoformat(),
            "initial_qty": 10.0,
            "procurement_cost": 50.0,
        },
        headers=admin_headers,
    )
    assert b1_res.status_code == 201
    b1_id = b1_res.json()["id"]

    # Batch 2: Expiring in 10 days (Quantity: 20)
    expiry_later = datetime.now(timezone.utc) + timedelta(days=10)
    b2_res = await client.post(
        "/api/v1/inventory/batches",
        json={
            "batch_number": "LOT-MILK-LATER-02",
            "product_id": prod_id,
            "vendor_id": vendor_id,
            "warehouse_id": wh_id,
            "expiry_date": expiry_later.isoformat(),
            "initial_qty": 20.0,
            "procurement_cost": 52.0,
        },
        headers=admin_headers,
    )
    assert b2_res.status_code == 201
    b2_id = b2_res.json()["id"]

    # 7. FEFO Allocation Test: Request 15 units
    # Expect: 10 units from Batch 1 (expiring sooner) + 5 units from Batch 2
    fefo_preview = await client.get(f"/api/v1/inventory/fefo-preview/{prod_id}?qty=15")
    assert fefo_preview.status_code == 200
    plan = fefo_preview.json()
    assert plan["is_fully_allocated"] is True
    assert plan["total_allocated_qty"] == 15.0
    assert len(plan["allocations"]) == 2
    assert plan["allocations"][0]["batch_id"] == b1_id
    assert plan["allocations"][0]["allocated_qty"] == 10.0
    assert plan["allocations"][1]["batch_id"] == b2_id
    assert plan["allocations"][1]["allocated_qty"] == 5.0

    # 8. Reserve Stock for Cart
    reserve_res = await client.post(
        "/api/v1/inventory/reserve",
        json={
            "reference_id": "cart_session_998877",
            "product_id": prod_id,
            "quantity": 15.0,
            "ttl_seconds": 600,
        },
    )
    assert reserve_res.status_code == 200
    assert reserve_res.json()["is_successful"] is True

    # Check Batch 1 available_qty is now 0 and reserved_qty is 10
    batches_res = await client.get(f"/api/v1/inventory/batches?product_id={prod_id}")
    batches_data = batches_res.json()
    b1_check = next(b for b in batches_data if b["id"] == b1_id)
    assert b1_check["available_qty"] == 0.0
    assert b1_check["reserved_qty"] == 10.0

    # 9. Release Stock (Simulate Cart Abandonment)
    release_res = await client.post(
        "/api/v1/inventory/release",
        json={"reference_id": "cart_session_998877"},
    )
    assert release_res.status_code == 200
    assert release_res.json()["success"] is True

    # Verify Stock Restored
    batches_restored = (await client.get(f"/api/v1/inventory/batches?product_id={prod_id}")).json()
    b1_restored = next(b for b in batches_restored if b["id"] == b1_id)
    assert b1_restored["available_qty"] == 10.0
    assert b1_restored["reserved_qty"] == 0.0
