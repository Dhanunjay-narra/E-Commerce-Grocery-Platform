"""Pydantic schemas for users, profiles, addresses, dietary preferences, and households."""
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")


class UserProfileUpdate(BaseModel):
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    preferred_language: Optional[str] = "en"
    preferred_currency: Optional[str] = "INR"
    substitution_preference: Optional[str] = "ASK_FIRST"  # ALWAYS_SUBSTITUTE, ASK_FIRST, NEVER_SUBSTITUTE


class UserProfileResponse(BaseModel):
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    preferred_language: str
    preferred_currency: str
    substitution_preference: str

    model_config = ConfigDict(from_attributes=True)


class UserAddressCreate(BaseModel):
    label: str = Field(default="Home", description="Home, Work, Other")
    recipient_name: str
    recipient_phone: str
    street_address: str
    apartment_suite: Optional[str] = None
    landmark: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False
    delivery_instructions: Optional[str] = None


class UserAddressUpdate(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    street_address: Optional[str] = None
    apartment_suite: Optional[str] = None
    landmark: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = None
    delivery_instructions: Optional[str] = None


class UserAddressResponse(BaseModel):
    id: str
    user_id: str
    label: str
    recipient_name: str
    recipient_phone: str
    street_address: str
    apartment_suite: Optional[str] = None
    landmark: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool
    delivery_instructions: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DietaryPreferenceUpdate(BaseModel):
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False
    is_dairy_free: bool = False
    is_organic_only: bool = False
    is_diabetic_friendly: bool = False
    allergies: Optional[str] = None


class DietaryPreferenceResponse(BaseModel):
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    is_dairy_free: bool
    is_organic_only: bool
    is_diabetic_friendly: bool
    allergies: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HouseholdMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    can_edit_list: bool
    can_order: bool
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HouseholdItemCreate(BaseModel):
    product_id: Optional[str] = None
    custom_name: Optional[str] = None
    quantity: float = 1.0
    unit: str = "pcs"


class HouseholdItemUpdate(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    is_checked: Optional[bool] = None


class HouseholdItemResponse(BaseModel):
    id: str
    household_id: str
    product_id: Optional[str] = None
    custom_name: Optional[str] = None
    quantity: float
    unit: str
    is_checked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HouseholdCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class HouseholdMemberAdd(BaseModel):
    email: EmailStr
    role: str = Field(default="MEMBER", description="ADMIN, MEMBER")
    can_edit_list: bool = True
    can_order: bool = True


class HouseholdResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    members: List[HouseholdMemberResponse] = []
    items: List[HouseholdItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str] = None
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    phone_verified: bool
    mfa_enabled: bool
    profile: Optional[UserProfileResponse] = None
    dietary_preference: Optional[DietaryPreferenceResponse] = None
    addresses: List[UserAddressResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
