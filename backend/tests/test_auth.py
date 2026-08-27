"""Authentication endpoint tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    # 1. Register new user
    register_payload = {
        "email": "customer@example.com",
        "password": "Password123!",
        "full_name": "Test Customer",
        "phone": "+919876543210",
        "role": "CUSTOMER",
    }
    reg_res = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert "refresh_token" in reg_data
    assert reg_data["user"]["email"] == "customer@example.com"
    assert reg_data["user"]["role"] == "CUSTOMER"

    # 2. Login with password
    login_payload = {
        "email_or_phone": "customer@example.com",
        "password": "Password123!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # 3. Test Invalid password
    bad_login_res = await client.post(
        "/api/v1/auth/login",
        json={"email_or_phone": "customer@example.com", "password": "WrongPassword!"},
    )
    assert bad_login_res.status_code == 401


@pytest.mark.asyncio
async def test_otp_flow(client: AsyncClient):
    # Request OTP
    otp_req = await client.post(
        "/api/v1/auth/otp/request",
        json={"identifier": "+919999988888", "purpose": "LOGIN"},
    )
    assert otp_req.status_code == 200

    # Verify OTP
    verify_req = await client.post(
        "/api/v1/auth/otp/verify",
        json={"identifier": "+919999988888", "otp_code": "123456", "purpose": "LOGIN", "full_name": "OTP User"},
    )
    assert verify_req.status_code == 200
    data = verify_req.json()
    assert "access_token" in data
    assert data["user"]["phone_verified"] is True
