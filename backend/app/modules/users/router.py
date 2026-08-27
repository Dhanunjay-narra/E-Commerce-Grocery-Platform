"""User Profile, Addresses, Dietary Preferences, and Household APIs."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.authentication.permissions import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import (
    UserDetailResponse,
    UserUpdate,
    UserProfileUpdate,
    UserProfileResponse,
    UserAddressCreate,
    UserAddressUpdate,
    UserAddressResponse,
    DietaryPreferenceUpdate,
    DietaryPreferenceResponse,
    HouseholdCreate,
    HouseholdMemberAdd,
    HouseholdResponse,
    HouseholdItemCreate,
    HouseholdItemUpdate,
    HouseholdItemResponse,
)
from app.modules.users.service import UserService, HouseholdService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserDetailResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full profile, default addresses, and dietary preferences for current user."""
    service = UserService(db)
    return await service.get_user_details(current_user.id)


@router.patch("/me", response_model=UserDetailResponse)
async def update_my_basic_info(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates customer name or phone number."""
    service = UserService(db)
    return await service.update_user(current_user.id, payload)


@router.patch("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates extended profile preferences (currency, language, substitution behavior)."""
    service = UserService(db)
    return await service.update_profile(current_user.id, payload)


@router.get("/me/addresses", response_model=List[UserAddressResponse])
async def list_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all saved delivery addresses for current user."""
    service = UserService(db)
    return await service.get_addresses(current_user.id)


@router.post("/me/addresses", response_model=UserAddressResponse, status_code=status.HTTP_201_CREATED)
async def add_address(
    payload: UserAddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Adds a new delivery address."""
    service = UserService(db)
    return await service.add_address(current_user.id, payload)


@router.patch("/me/addresses/{address_id}", response_model=UserAddressResponse)
async def update_address(
    address_id: str,
    payload: UserAddressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates an existing delivery address."""
    service = UserService(db)
    return await service.update_address(current_user.id, address_id, payload)


@router.delete("/me/addresses/{address_id}")
async def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft deletes a saved delivery address."""
    service = UserService(db)
    await service.delete_address(current_user.id, address_id)
    return {"success": True, "message": "Address deleted successfully."}


@router.post("/me/addresses/{address_id}/default", response_model=UserAddressResponse)
async def set_default_address(
    address_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sets a given address as the primary/default delivery location."""
    service = UserService(db)
    return await service.set_default_address(current_user.id, address_id)


@router.get("/me/dietary-preferences", response_model=DietaryPreferenceResponse)
async def get_dietary_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves dietary preferences, vegan/veg flags, and allergy exclusions."""
    service = UserService(db)
    return await service.get_dietary_preferences(current_user.id)


@router.put("/me/dietary-preferences", response_model=DietaryPreferenceResponse)
async def update_dietary_preferences(
    payload: DietaryPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates dietary preferences and allergy filters."""
    service = UserService(db)
    return await service.update_dietary_preferences(current_user.id, payload)


# Household Collaboration Endpoints
@router.get("/me/household", response_model=HouseholdResponse)
async def get_my_household(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Gets current user's shared household and list of family members."""
    service = HouseholdService(db)
    household = await service.get_household(current_user.id)
    if not household:
        return {"id": "", "name": "", "owner_id": "", "members": [], "items": []}
    return household


@router.post("/me/household", response_model=HouseholdResponse, status_code=status.HTTP_201_CREATED)
async def create_household(
    payload: HouseholdCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new collaborative grocery household."""
    service = HouseholdService(db)
    return await service.create_household(current_user.id, payload)


@router.post("/me/household/members")
async def invite_household_member(
    payload: HouseholdMemberAdd,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invites a family member to the household shopping list."""
    service = HouseholdService(db)
    await service.add_member(current_user.id, payload)
    return {"success": True, "message": f"Successfully added {payload.email} to your household."}


@router.delete("/me/household/members/{member_id}")
async def remove_household_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Removes a member from the household."""
    service = HouseholdService(db)
    await service.remove_member(current_user.id, member_id)
    return {"success": True, "message": "Member removed from household."}


@router.get("/me/household/items", response_model=List[HouseholdItemResponse])
async def list_household_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists collaborative shopping list items for the household."""
    service = HouseholdService(db)
    items = await service.get_items(current_user.id)
    return items


@router.post("/me/household/items", response_model=HouseholdItemResponse, status_code=status.HTTP_201_CREATED)
async def add_household_item(
    payload: HouseholdItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Adds an item to the shared household shopping list."""
    service = HouseholdService(db)
    return await service.add_item(current_user.id, payload)


@router.patch("/me/household/items/{item_id}", response_model=HouseholdItemResponse)
async def update_household_item(
    item_id: str,
    payload: HouseholdItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates quantity or marks a household item as checked off."""
    service = HouseholdService(db)
    return await service.update_item(current_user.id, item_id, payload)


@router.delete("/me/household/items/{item_id}")
async def delete_household_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes an item from the shared shopping list."""
    service = HouseholdService(db)
    await service.delete_item(current_user.id, item_id)
    return {"success": True, "message": "Item removed from list."}


@router.get("/me/export-data")
async def export_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GDPR Data portability: exports full account data, preferences, and addresses."""
    service = UserService(db)
    return await service.export_user_data(current_user.id)


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GDPR Right-to-be-forgotten: deactivates and soft-deletes user account."""
    service = UserService(db)
    await service.delete_account(current_user.id)
    return {"success": True, "message": "Account successfully scheduled for deletion and sessions revoked."}
