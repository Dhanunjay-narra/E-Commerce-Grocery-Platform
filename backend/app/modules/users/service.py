"""User profile, address, and household collaboration business service layer."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ConflictError, PermissionDeniedError, ValidationError
from app.modules.users.models import User, UserAddress, UserProfile, DietaryPreference, Household, HouseholdMember, HouseholdShoppingItem
from app.modules.users.schemas import (
    UserUpdate,
    UserProfileUpdate,
    UserAddressCreate,
    UserAddressUpdate,
    DietaryPreferenceUpdate,
    HouseholdCreate,
    HouseholdMemberAdd,
    HouseholdItemCreate,
    HouseholdItemUpdate,
    UserDetailResponse,
    HouseholdResponse,
    HouseholdMemberResponse,
)
from app.modules.users.repository import UserRepository
from app.modules.authentication.repository import AuthRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)

    async def get_user_details(self, user_id: str) -> UserDetailResponse:
        user = await self.repo.get_by_id_with_relations(user_id)
        if not user:
            raise EntityNotFoundError("User profile not found.")
        return UserDetailResponse.model_validate(user)

    async def update_user(self, user_id: str, payload: UserUpdate) -> UserDetailResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User not found.")

        if payload.phone and payload.phone != user.phone:
            existing = await self.auth_repo.get_user_by_phone(payload.phone)
            if existing:
                raise ConflictError("This phone number is already attached to another account.")
            user.phone_verified = False

        await self.repo.update_user(user, full_name=payload.full_name, phone=payload.phone)
        return await self.get_user_details(user_id)

    async def update_profile(self, user_id: str, payload: UserProfileUpdate) -> UserProfile:
        return await self.repo.update_profile(user_id, payload)

    async def get_addresses(self, user_id: str) -> List[UserAddress]:
        return await self.repo.get_addresses(user_id)

    async def add_address(self, user_id: str, payload: UserAddressCreate) -> UserAddress:
        return await self.repo.create_address(user_id, payload)

    async def update_address(self, user_id: str, address_id: str, payload: UserAddressUpdate) -> UserAddress:
        address = await self.repo.get_address_by_id(address_id, user_id)
        if not address:
            raise EntityNotFoundError("Address not found.")
        return await self.repo.update_address(address, payload)

    async def delete_address(self, user_id: str, address_id: str) -> None:
        address = await self.repo.get_address_by_id(address_id, user_id)
        if not address:
            raise EntityNotFoundError("Address not found.")
        await self.repo.delete_address(address)

    async def set_default_address(self, user_id: str, address_id: str) -> UserAddress:
        address = await self.repo.set_default_address(address_id, user_id)
        if not address:
            raise EntityNotFoundError("Address not found.")
        return address

    async def get_dietary_preferences(self, user_id: str) -> DietaryPreference:
        return await self.repo.get_or_create_dietary_preferences(user_id)

    async def update_dietary_preferences(self, user_id: str, payload: DietaryPreferenceUpdate) -> DietaryPreference:
        return await self.repo.update_dietary_preferences(user_id, payload)

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """GDPR compliance: bundle full user identity, addresses, and history."""
        user = await self.repo.get_by_id_with_relations(user_id)
        if not user:
            raise EntityNotFoundError("User not found.")

        return {
            "account": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": str(user.created_at),
            },
            "profile": {
                "language": user.profile.preferred_language if user.profile else "en",
                "currency": user.profile.preferred_currency if user.profile else "INR",
                "substitution_preference": user.profile.substitution_preference if user.profile else "ASK_FIRST",
            },
            "addresses": [
                {
                    "label": a.label,
                    "recipient": a.recipient_name,
                    "phone": a.recipient_phone,
                    "street": a.street_address,
                    "city": a.city,
                    "postal_code": a.postal_code,
                }
                for a in user.addresses
            ],
            "dietary_preferences": {
                "is_vegetarian": user.dietary_preference.is_vegetarian if user.dietary_preference else False,
                "is_vegan": user.dietary_preference.is_vegan if user.dietary_preference else False,
                "allergies": user.dietary_preference.allergies if user.dietary_preference else None,
            },
        }

    async def delete_account(self, user_id: str) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User not found.")
        user.soft_delete()
        await self.auth_repo.revoke_all_user_sessions(user_id)


class HouseholdService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)

    async def get_household(self, user_id: str) -> Optional[HouseholdResponse]:
        household = await self.repo.get_user_household(user_id)
        if not household:
            return None

        members_dto = [
            HouseholdMemberResponse(
                id=m.id,
                user_id=m.user_id,
                role=m.role,
                can_edit_list=m.can_edit_list,
                can_order=m.can_order,
                user_name=m.user.full_name if m.user else None,
                user_email=m.user.email if m.user else None,
            )
            for m in household.members
        ]

        return HouseholdResponse(
            id=household.id,
            name=household.name,
            owner_id=household.owner_id,
            members=members_dto,
            items=[HouseholdItemCreate.model_validate(item) for item in household.items] if False else [],
        )

    async def create_household(self, user_id: str, payload: HouseholdCreate) -> HouseholdResponse:
        existing = await self.repo.get_user_household(user_id)
        if existing:
            raise ConflictError("You are already part of an active household.")

        household = await self.repo.create_household(owner_id=user_id, name=payload.name)
        res = await self.repo.get_user_household(user_id)
        return await self.get_household(user_id)  # type: ignore

    async def add_member(self, user_id: str, payload: HouseholdMemberAdd) -> None:
        household = await self.repo.get_user_household(user_id)
        if not household:
            raise EntityNotFoundError("You do not belong to a household.")

        # Check permissions
        current_member = next((m for m in household.members if m.user_id == user_id), None)
        if not current_member or current_member.role not in ["OWNER", "ADMIN"]:
            raise PermissionDeniedError("Only household owners or admins can invite new members.")

        invited_user = await self.auth_repo.get_user_by_email(payload.email)
        if not invited_user:
            raise EntityNotFoundError(f"No user found with email {payload.email}. They must create an account first.")

        # Check if already a member
        if any(m.user_id == invited_user.id for m in household.members):
            raise ConflictError("User is already a member of this household.")

        await self.repo.add_household_member(
            household_id=household.id,
            user_id=invited_user.id,
            role=payload.role,
            can_edit=payload.can_edit_list,
            can_order=payload.can_order,
        )

    async def remove_member(self, user_id: str, member_id: str) -> None:
        household = await self.repo.get_user_household(user_id)
        if not household:
            raise EntityNotFoundError("You do not belong to a household.")

        current_member = next((m for m in household.members if m.user_id == user_id), None)
        if not current_member or current_member.role not in ["OWNER", "ADMIN"]:
            raise PermissionDeniedError("Only household owners or admins can remove members.")

        target = next((m for m in household.members if m.id == member_id), None)
        if not target:
            raise EntityNotFoundError("Household member not found.")

        if target.role == "OWNER":
            raise PermissionDeniedError("The household owner cannot be removed.")

        await self.repo.remove_household_member(household.id, member_id)

    async def get_items(self, user_id: str) -> List[HouseholdShoppingItem]:
        household = await self.repo.get_user_household(user_id)
        if not household:
            raise EntityNotFoundError("You do not belong to a household.")
        return await self.repo.get_household_items(household.id)

    async def add_item(self, user_id: str, payload: HouseholdItemCreate) -> HouseholdShoppingItem:
        household = await self.repo.get_user_household(user_id)
        if not household:
            raise EntityNotFoundError("You must create or join a household first.")
        return await self.repo.add_household_item(household.id, user_id, payload)

    async def update_item(self, user_id: str, item_id: str, payload: HouseholdItemUpdate) -> HouseholdShoppingItem:
        household = await self.repo.get_user_household(user_id)
        if not household:
            raise EntityNotFoundError("Household not found.")
        item = await self.repo.update_household_item(item_id, household.id, payload)
        if not item:
            raise EntityNotFoundError("Shopping item not found in your household.")
        return item

    async def delete_item(self, user_id: str, item_id: str) -> None:
        household = await self.repo.get_user_household(user_id)
        if not household:
            raise EntityNotFoundError("Household not found.")
        success = await self.repo.delete_household_item(item_id, household.id)
        if not success:
            raise EntityNotFoundError("Shopping item not found in your household.")
