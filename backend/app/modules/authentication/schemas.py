from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: str = Field(..., min_length=2, max_length=150)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    role: Optional[str] = Field(default="CUSTOMER")


class LoginRequest(BaseModel):
    email_or_phone: str
    password: str
    device_info: Optional[str] = None


class OTPRequest(BaseModel):
    identifier: str = Field(..., description="Phone number or Email address")
    purpose: str = Field(default="LOGIN", description="LOGIN, REGISTER, RESET_PASSWORD, DELIVERY_POD")


class OTPVerifyRequest(BaseModel):
    identifier: str
    otp_code: str = Field(..., min_length=4, max_length=10)
    purpose: str = Field(default="LOGIN")
    full_name: Optional[str] = None  # For registration if user does not exist yet


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "AuthUserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    identifier: str
    otp_code: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class SessionResponse(BaseModel):
    id: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    last_active_at: datetime
    is_current: bool = False


class AuthUserResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    phone_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


TokenResponse.model_rebuild()
