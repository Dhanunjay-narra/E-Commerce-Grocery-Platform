"""Notifications and Executive Admin Analytics Tests."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.notifications.service import NotificationService
from app.modules.notifications.schemas import NotificationCreate
from app.modules.admin.service import AdminService


@pytest.mark.asyncio
async def test_notifications_and_admin_analytics_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. Register Admin & Customer
    admin_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "super_admin@freshcart.com", "password": "Password123!", "full_name": "Executive Officer", "role": "SUPER_ADMIN"},
    )
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    cust_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "notif_user@freshcart.com", "password": "Password123!", "full_name": "Rohan Gupta", "role": "CUSTOMER"},
    )
    cust_token = cust_res.json()["access_token"]
    cust_id = cust_res.json()["user"]["id"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 2. Executive Dashboard Analytics
    dash_res = await client.get("/api/v1/admin/analytics/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200
    metrics = dash_res.json()
    assert "gross_merchandise_value" in metrics
    assert "total_orders_count" in metrics
    assert metrics["active_customers_count"] >= 1

    # 3. Notification Flow: Read empty, Add, Read, Mark All Read
    n_service = NotificationService(db_session)
    await n_service.send_notification(
        NotificationCreate(
            user_id=cust_id,
            title="Your Order has Arrived!",
            body="Your fresh grocery package was delivered successfully.",
            type="OUT_FOR_DELIVERY",
        )
    )
    await db_session.commit()

    # Customer queries notifications
    notif_list = await client.get("/api/v1/notifications", headers=cust_headers)
    assert notif_list.status_code == 200
    items = notif_list.json()
    assert len(items) == 1
    assert items[0]["is_read"] is False
    notif_id = items[0]["id"]

    # Mark as read
    read_res = await client.patch(f"/api/v1/notifications/{notif_id}/read", headers=cust_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # 4. Audit Log Verification
    adm_service = AdminService(db_session)
    await adm_service.log_action(
        actor_id="admin_01",
        actor_email="super_admin@freshcart.com",
        actor_role="SUPER_ADMIN",
        action="KYC_APPROVED",
        entity_type="VENDOR",
        entity_id="vend_123",
        changes={"status": "APPROVED", "remarks": "Documents verified"},
    )
    await db_session.commit()

    # Admin reads audit logs
    audit_res = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "KYC_APPROVED"
    assert logs[0]["entity_type"] == "VENDOR"
