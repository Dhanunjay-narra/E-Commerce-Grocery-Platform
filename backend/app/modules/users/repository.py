"""User domain database repository."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import (
    User,
    UserProfile,
    UserAddress,
    DietaryPreference,
    Household,
    HouseholdMember,
    HouseholdShoppingItem,
)
from app.modules.users.schemas import (
    UserAddressCreate,
    UserAddressUpdate,
    UserProfileUpdate,
    DietaryPreferenceUpdate,
    HouseholdItemCreate,
    HouseholdItemUpdate,
)


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        query = select(User).where(and_(User.id == user_id, User.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, user_id: str) -> Optional[User]:
        query = (
            select(User)
            .where(and_(User.id == user_id, User.is_deleted == False))
            .options(
                selectinload(User.profile),
                selectinload(User.dietary_preference),
                selectinload(User.addresses),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_user(self, user: User, full_name: Optional[str] = None, phone: Optional[str] = None) -> User:
        if full_name:
            user.full_name = full_name
        if phone:
            user.phone = phone
        await self.db.flush()
        return user

    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.flush()
        return profile

    async def update_profile(self, user_id: str, payload: UserProfileUpdate) -> UserProfile:
        profile = await self.get_or_create_profile(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(profile, field, val)
        await self.db.flush()
        return profile

    async def get_addresses(self, user_id: str) -> List[UserAddress]:
        query = (
            select(UserAddress)
            .where(and_(UserAddress.user_id == user_id, UserAddress.is_deleted == False))
            .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_address_by_id(self, address_id: str, user_id: str) -> Optional[UserAddress]:
        query = select(UserAddress).where(
            and_(UserAddress.id == address_id, UserAddress.user_id == user_id, UserAddress.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_address(self, user_id: str, payload: UserAddressCreate) -> UserAddress:
        if payload.is_default:
            await self.db.execute(
                update(UserAddress).where(UserAddress.user_id == user_id).values(is_default=False)
            )

        # If it's the first address, make it default automatically
        existing = await self.get_addresses(user_id)
        is_first = len(existing) == 0

        address = UserAddress(
            user_id=user_id,
            label=payload.label,
            recipient_name=payload.recipient_name,
            recipient_phone=payload.recipient_phone,
            street_address=payload.street_address,
            apartment_suite=payload.apartment_suite,
            landmark=payload.landmark,
            city=payload.city,
            state=payload.state,
            postal_code=payload.postal_code,
            country=payload.country,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_default=payload.is_default or is_first,
            delivery_instructions=payload.delivery_instructions,
        )
        self.db.add(address)
        await self.db.flush()
        return address

    async def update_address(self, address: UserAddress, payload: UserAddressUpdate) -> UserAddress:
        if payload.is_default:
            await self.db.execute(
                update(UserAddress).where(UserAddress.user_id == address.user_id).values(is_default=False)
            )
        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(address, field, val)
        await self.db.flush()
        return address

    async def set_default_address(self, address_id: str, user_id: str) -> Optional[UserAddress]:
        await self.db.execute(
            update(UserAddress).where(UserAddress.user_id == user_id).values(is_default=False)
        )
        address = await self.get_address_by_id(address_id, user_id)
        if address:
            address.is_default = True
            await self.db.flush()
        return address

    async def delete_address(self, address: UserAddress) -> None:
        address.soft_delete()
        await self.db.flush()

    async def get_or_create_dietary_preferences(self, user_id: str) -> DietaryPreference:
        query = select(DietaryPreference).where(DietaryPreference.user_id == user_id)
        result = await self.db.execute(query)
        pref = result.scalar_one_or_none()
        if not pref:
            pref = DietaryPreference(user_id=user_id)
            self.db.add(pref)
            await self.db.flush()
        return pref

    async def update_dietary_preferences(self, user_id: str, payload: DietaryPreferenceUpdate) -> DietaryPreference:
        pref = await self.get_or_create_dietary_preferences(user_id)
        update_data = payload.model_dump()
        for field, val in update_data.items():
            setattr(pref, field, val)
        await self.db.flush()
        return pref

    # Household repository methods
    async def get_user_household(self, user_id: str) -> Optional[Household]:
        query = (
            select(Household)
            .join(HouseholdMember, HouseholdMember.household_id == Household.id)
            .where(and_(HouseholdMember.user_id == user_id, Household.is_deleted == False))
            .options(
                selectinload(Household.members).selectinload(HouseholdMember.user),
                selectinload(Household.items),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_household(self, owner_id: str, name: str) -> Household:
        household = Household(name=name, owner_id=owner_id)
        self.db.add(household)
        await self.db.flush()

        member = HouseholdMember(
            household_id=household.id,
            user_id=owner_id,
            role="OWNER",
            can_edit_list=True,
            can_order=True,
        )
        self.db.add(member)
        await self.db.flush()
        return household

    async def add_household_member(
        self, household_id: str, user_id: str, role: str = "MEMBER", can_edit: bool = True, can_order: bool = True
    ) -> HouseholdMember:
        member = HouseholdMember(
            household_id=household_id,
            user_id=user_id,
            role=role,
            can_edit_list=can_edit,
            can_order=can_order,
        )
        self.db.add(member)
        await self.db.flush()
        return member

    async def remove_household_member(self, household_id: str, member_id: str) -> None:
        stmt = delete(HouseholdMember).where(
            and_(HouseholdMember.household_id == household_id, HouseholdMember.id == member_id)
        )
        await self.db.execute(stmt)

    async def get_household_items(self, household_id: str) -> List[HouseholdShoppingItem]:
        query = (
            select(HouseholdShoppingItem)
            .where(HouseholdShoppingItem.household_id == household_id)
            .order_by(HouseholdShoppingItem.is_checked.asc(), HouseholdShoppingItem.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_household_item(self, household_id: str, user_id: str, payload: HouseholdItemCreate) -> HouseholdShoppingItem:
        item = HouseholdShoppingItem(
            household_id=household_id,
            product_id=payload.product_id,
            custom_name=payload.custom_name,
            quantity=payload.quantity,
            unit=payload.unit,
            added_by_user_id=user_id,
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def update_household_item(self, item_id: str, household_id: str, payload: HouseholdItemUpdate) -> Optional[HouseholdShoppingItem]:
        query = select(HouseholdShoppingItem).where(
            and_(HouseholdShoppingItem.id == item_id, HouseholdShoppingItem.household_id == household_id)
        )
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        if not item:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(item, field, val)
        await self.db.flush()
        return item

    async def delete_household_item(self, item_id: str, household_id: str) -> bool:
        stmt = delete(HouseholdShoppingItem).where(
            and_(HouseholdShoppingItem.id == item_id, HouseholdShoppingItem.household_id == household_id)
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0
