"""Vendor onboarding, KYC moderation, and store location management service."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ConflictError, PermissionDeniedError, ValidationError
from app.modules.vendors.models import Vendor, VendorStore, VendorPayout
from app.modules.vendors.schemas import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorDetailResponse,
    VendorStoreCreate,
    VendorStoreUpdate,
    VendorStoreResponse,
    VendorKYCReviewRequest,
    VendorPayoutResponse,
)
from app.modules.vendors.repository import VendorRepository
from app.modules.categories.service import slugify


class VendorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = VendorRepository(db)

    async def list_vendors(self, kyc_status: Optional[str] = None) -> List[VendorDetailResponse]:
        vendors = await self.repo.list_vendors(kyc_status=kyc_status)
        return [self._map_detail_dto(v) for v in vendors]

    async def get_by_id_or_slug(self, identifier: str) -> VendorDetailResponse:
        vendor = await self.repo.get_by_slug(identifier) or await self.repo.get_by_id(identifier)
        if not vendor:
            raise EntityNotFoundError(f"Vendor '{identifier}' not found.")
        return self._map_detail_dto(vendor)

    async def get_by_owner_id(self, owner_id: str) -> Optional[VendorDetailResponse]:
        vendor = await self.repo.get_by_owner_id(owner_id)
        if not vendor:
            return None
        return self._map_detail_dto(vendor)

    async def register(self, owner_id: str, payload: VendorCreate) -> VendorDetailResponse:
        existing = await self.repo.get_by_owner_id(owner_id)
        if existing:
            raise ConflictError("You have already registered a vendor store on FreshCart.")

        slug = slugify(payload.business_name)
        existing_slug = await self.repo.get_by_slug(slug)
        if existing_slug:
            import time
            slug = f"{slug}-{int(time.time())}"

        vendor = await self.repo.create(owner_id, payload, slug=slug)
        return self._map_detail_dto(vendor)

    async def review_kyc(self, vendor_id: str, payload: VendorKYCReviewRequest) -> VendorDetailResponse:
        vendor = await self.repo.get_by_id(vendor_id)
        if not vendor:
            raise EntityNotFoundError("Vendor not found.")

        updated = await self.repo.update_kyc(
            vendor,
            status=payload.kyc_status.upper(),
            notes=payload.kyc_notes,
            commission=payload.commission_rate,
        )
        return self._map_detail_dto(updated)

    async def add_store(self, vendor_id: str, payload: VendorStoreCreate) -> VendorStoreResponse:
        vendor = await self.repo.get_by_id(vendor_id)
        if not vendor:
            raise EntityNotFoundError("Vendor not found.")

        store = await self.repo.create_store(vendor_id, payload)
        return VendorStoreResponse.model_validate(store)

    async def list_payouts(self, vendor_id: str) -> List[VendorPayoutResponse]:
        payouts = await self.repo.list_payouts(vendor_id)
        return [VendorPayoutResponse.model_validate(p) for p in payouts]

    def _map_detail_dto(self, v: Vendor) -> VendorDetailResponse:
        stores_dto = [VendorStoreResponse.model_validate(s) for s in v.stores if not s.is_deleted]
        return VendorDetailResponse(
            id=v.id,
            business_name=v.business_name,
            slug=v.slug,
            owner_id=v.owner_id,
            email=v.email,
            phone=v.phone,
            tax_id=v.tax_id,
            kyc_status=v.kyc_status,
            commission_rate=v.commission_rate,
            is_active=v.is_active,
            rating_average=v.rating_average,
            rating_count=v.rating_count,
            created_at=v.created_at,
            stores=stores_dto,
        )
