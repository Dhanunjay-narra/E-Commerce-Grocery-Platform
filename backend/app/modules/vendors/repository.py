"""Vendor marketplace database repository layer."""
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.vendors.models import Vendor, VendorStore, VendorPayout
from app.modules.vendors.schemas import VendorCreate, VendorUpdate, VendorStoreCreate, VendorStoreUpdate


class VendorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, vendor_id: str) -> Optional[Vendor]:
        query = (
            select(Vendor)
            .where(and_(Vendor.id == vendor_id, Vendor.is_deleted == False))
            .options(selectinload(Vendor.stores), selectinload(Vendor.payouts))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_owner_id(self, owner_id: str) -> Optional[Vendor]:
        query = (
            select(Vendor)
            .where(and_(Vendor.owner_id == owner_id, Vendor.is_deleted == False))
            .options(selectinload(Vendor.stores))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Vendor]:
        query = (
            select(Vendor)
            .where(and_(Vendor.slug == slug.lower().strip(), Vendor.is_deleted == False))
            .options(selectinload(Vendor.stores))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_vendors(self, kyc_status: Optional[str] = None, only_active: bool = True) -> List[Vendor]:
        conditions = [Vendor.is_deleted == False]
        if only_active:
            conditions.append(Vendor.is_active == True)
        if kyc_status:
            conditions.append(Vendor.kyc_status == kyc_status)

        query = (
            select(Vendor)
            .where(and_(*conditions))
            .options(selectinload(Vendor.stores))
            .order_by(Vendor.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, owner_id: str, payload: VendorCreate, slug: str) -> Vendor:
        vendor = Vendor(
            business_name=payload.business_name,
            slug=slug,
            owner_id=owner_id,
            email=payload.email.lower().strip(),
            phone=payload.phone.strip(),
            tax_id=payload.tax_id,
            kyc_status="PENDING",
        )
        self.db.add(vendor)
        await self.db.flush()

        if payload.store:
            store = VendorStore(
                vendor_id=vendor.id,
                store_name=payload.store.store_name,
                address_street=payload.store.address_street,
                city=payload.store.city,
                state=payload.store.state,
                postal_code=payload.store.postal_code,
                latitude=payload.store.latitude,
                longitude=payload.store.longitude,
                delivery_radius_km=payload.store.delivery_radius_km,
                opens_at=payload.store.opens_at,
                closes_at=payload.store.closes_at,
            )
            self.db.add(store)
            await self.db.flush()

        return await self.get_by_id(vendor.id)  # type: ignore

    async def update_kyc(self, vendor: Vendor, status: str, notes: Optional[str], commission: Optional[float]) -> Vendor:
        vendor.kyc_status = status
        if notes:
            vendor.kyc_notes = notes
        if commission is not None:
            vendor.commission_rate = commission
        await self.db.flush()
        return vendor

    async def create_store(self, vendor_id: str, payload: VendorStoreCreate) -> VendorStore:
        store = VendorStore(
            vendor_id=vendor_id,
            store_name=payload.store_name,
            address_street=payload.address_street,
            city=payload.city,
            state=payload.state,
            postal_code=payload.postal_code,
            latitude=payload.latitude,
            longitude=payload.longitude,
            delivery_radius_km=payload.delivery_radius_km,
            opens_at=payload.opens_at,
            closes_at=payload.closes_at,
        )
        self.db.add(store)
        await self.db.flush()
        return store

    async def list_payouts(self, vendor_id: str) -> List[VendorPayout]:
        query = select(VendorPayout).where(VendorPayout.vendor_id == vendor_id).order_by(VendorPayout.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
