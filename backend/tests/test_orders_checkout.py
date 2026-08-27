"""End-to-End Grocery Checkout, Delivery Slot, Variable-Weight Picking, and Order State Machine Tests."""
from datetime import datetime, timezone, timedelta, date
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_order_checkout_lifecycle(client: AsyncClient):
    # 1. Register Customer & Admin
    admin_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "admin_order@freshcart.com", "password": "Password123!", "full_name": "Admin Ops", "role": "ADMIN"},
    )
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    cust_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "customer_order@freshcart.com", "password": "Password123!", "full_name": "Rajesh Kumar", "role": "CUSTOMER"},
    )
    cust_token = cust_res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Add Delivery Address
    addr_res = await client.post(
        "/api/v1/users/me/addresses",
        json={
            "label": "Home",
            "recipient_name": "Rajesh Kumar",
            "recipient_phone": "+919876543210",
            "street_address": "Villa 14, Palm Meadows",
            "city": "Hyderabad",
            "state": "Telangana",
            "postal_code": "500084",
            "is_default": True,
        },
        headers=cust_headers,
    )
    assert addr_res.status_code == 201
    addr_id = addr_res.json()["id"]

    # 3. Create Delivery Zone
    zone_res = await client.post(
        "/api/v1/shipping/zones",
        json={
            "name": "Hyderabad West Zone",
            "code": "HYD-WEST",
            "city": "Hyderabad",
            "state": "Telangana",
            "center_latitude": 17.44,
            "center_longitude": 78.37,
            "radius_km": 15.0,
            "base_fee": 30.0,
        },
        headers=admin_headers,
    )
    assert zone_res.status_code == 201
    zone_id = zone_res.json()["id"]

    # 4. Create Category & Variable-Weight Product (Tomatoes)
    cat_res = await client.post("/api/v1/categories", json={"name": "Organic Veggies"}, headers=admin_headers)
    cat_id = cat_res.json()["id"]

    prod_res = await client.post(
        "/api/v1/products",
        json={
            "sku": "VEG-TOM-RED-1KG",
            "name": "Organic Hybrid Red Tomatoes",
            "brand": "FarmDirect",
            "category_id": cat_id,
            "unit": "kg",
            "base_price": 50.0,
            "sale_price": 40.0,
            "is_variable_weight": True,
            "weight_increment": 0.5,
            "weight_tolerance_pct": 15.0,
        },
        headers=admin_headers,
    )
    prod_id = prod_res.json()["id"]

    # Add Batch Stock (100 kg)
    exp = datetime.now(timezone.utc) + timedelta(days=5)
    await client.post(
        "/api/v1/inventory/batches",
        json={
            "batch_number": "LOT-TOM-ORD-01",
            "product_id": prod_id,
            "expiry_date": exp.isoformat(),
            "initial_qty": 100.0,
        },
        headers=admin_headers,
    )

    # 5. Customer Adds 1.0 kg Tomatoes to Cart
    await client.post(
        "/api/v1/cart/items",
        json={"product_id": prod_id, "quantity": 1.0},
        headers=cust_headers,
    )

    # 6. Check Available Delivery Slots
    slots_res = await client.get(f"/api/v1/shipping/slots/available?zone_id={zone_id}&slot_date={date.today().isoformat()}")
    assert slots_res.status_code == 200
    slots = slots_res.json()
    assert len(slots) >= 1
    selected_slot_id = slots[0]["id"]

    # 7. Customer Checkout with Cash on Delivery
    checkout_payload = {
        "delivery_address_id": addr_id,
        "delivery_slot_id": selected_slot_id,
        "payment_method": "CASH_ON_DELIVERY",
        "substitution_preference": "ASK_FIRST",
        "customer_notes": "Please ring bell twice.",
    }
    checkout_res = await client.post("/api/v1/orders/checkout", json=checkout_payload, headers=cust_headers)
    assert checkout_res.status_code == 201
    order_data = checkout_res.json()
    order_id = order_data["id"]
    assert order_data["status"] == "PAYMENT_VERIFIED"
    assert len(order_data["items"]) == 1
    assert order_data["shipment"] is not None
    shipment_id = order_data["shipment"]["id"]
    delivery_otp = order_data["shipment"]["delivery_otp"]

    # 8. Order Fulfillment: Move to PICKING
    await client.post(
        f"/api/v1/orders/{order_id}/transition-status",
        json={"new_status": "PROCESSING"},
        headers=admin_headers,
    )
    await client.post(
        f"/api/v1/orders/{order_id}/transition-status",
        json={"new_status": "PICKING"},
        headers=admin_headers,
    )

    # 9. Picker Weighs Produce: 1.08 kg on scale instead of 1.00 kg
    item_id = order_data["items"][0]["id"]
    pick_res = await client.post(
        f"/api/v1/orders/{order_id}/pick-item",
        json={"order_item_id": item_id, "actual_picked_qty": 1.08, "item_status": "PICKED"},
        headers=admin_headers,
    )
    assert pick_res.status_code == 200
    picked_item = pick_res.json()["items"][0]
    assert picked_item["picked_qty"] == 1.08
    assert picked_item["final_item_total"] == 43.2  # 1.08 * 40.0 = 43.2

    # 10. Move to PACKED (Triggers automated reconciliation)
    packed_res = await client.post(
        f"/api/v1/orders/{order_id}/transition-status",
        json={"new_status": "PACKED"},
        headers=admin_headers,
    )
    assert packed_res.status_code == 200
    assert packed_res.json()["final_adjusted_total"] is not None

    # 11. Move to READY_FOR_DISPATCH & OUT_FOR_DELIVERY
    await client.post(
        f"/api/v1/orders/{order_id}/transition-status",
        json={"new_status": "READY_FOR_DISPATCH"},
        headers=admin_headers,
    )
    await client.post(
        f"/api/v1/orders/{order_id}/transition-status",
        json={"new_status": "OUT_FOR_DELIVERY"},
        headers=admin_headers,
    )

    # 12. Complete Proof of Delivery at Doorstep with 4-Digit OTP
    pod_res = await client.post(
        f"/api/v1/shipping/shipments/{shipment_id}/verify-pod",
        json={"otp": delivery_otp},
    )
    assert pod_res.status_code == 200
    assert pod_res.json()["status"] == "DELIVERED"

    # Transition order to DELIVERED
    delivered_res = await client.post(
        f"/api/v1/orders/{order_id}/transition-status",
        json={"new_status": "DELIVERED"},
        headers=admin_headers,
    )
    assert delivered_res.status_code == 200
    assert delivered_res.json()["status"] == "DELIVERED"

    # 13. Download / View Tax Invoice
    inv_res = await client.get(f"/api/v1/orders/{order_id}/invoice")
    assert inv_res.status_code == 200
    inv = inv_res.json()
    assert inv["order_number"] == order_data["order_number"]
    assert inv["customer_name"] == "Rajesh Kumar"
    assert len(inv["items"]) == 1
