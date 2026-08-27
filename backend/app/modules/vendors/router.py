"""Multi-Vendor Marketplace and Store Management API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import get_current_user, require_role
from app.modules.users.models import User
from app.modules.vendors.schemas import (
    VendorCreate,
    VendorResponse,
    VendorDetailResponse,
    VendorStoreCreate,
    VendorStoreResponse,
    VendorKYCReviewRequest,
    VendorPayoutResponse,
)
from app.modules.vendors.service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get("", response_model=List[VendorDetailResponse])
async def list_vendors(
    kyc_status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lists marketplace vendors with optional KYC filter."""
    service = VendorService(db)
    return await service.list_vendors(kyc_status=kyc_status)


@router.get("/me/profile", response_model=VendorDetailResponse)
async def get_my_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Vendor Portal: Retrieves the authenticated vendor owner's store profile."""
    service = VendorService(db)
    vendor = await service.get_by_owner_id(current_user.id)
    if not vendor:
        return {"id": "", "business_name": "Unregistered", "slug": "", "owner_id": current_user.id, "email": current_user.email, "phone": "", "kyc_status": "NONE", "commission_rate": 8.5, "is_active": False, "rating_average": 0.0, "rating_count": 0, "stores": [], "created_at": current_user.created_at}
    return vendor


@router.get("/{id_or_slug}", response_model=VendorDetailResponse)
async def get_vendor_detail(
    id_or_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves vendor details and active store locations."""
    service = VendorService(db)
    return await service.get_by_id_or_slug(id_or_slug)


@router.post("/register", response_model=VendorDetailResponse, status_code=status.HTTP_201_CREATED)
async def register_vendor(
    payload: VendorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Onboards a new merchant vendor onto the marketplace."""
    service = VendorService(db)
    current_user.role = UserRole.VENDOR_OWNER.value
    await db.flush()
    return await service.register(current_user.id, payload)


@router.patch("/{vendor_id}/kyc", response_model=VendorDetailResponse)
async def review_vendor_kyc(
    vendor_id: str,
    payload: VendorKYCReviewRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin endpoint to approve, reject, or assign custom commission to a vendor."""
    service = VendorService(db)
    return await service.review_kyc(vendor_id, payload)


@router.post("/me/stores", response_model=VendorStoreResponse, status_code=status.HTTP_201_CREATED)
async def add_vendor_store(
    payload: VendorStoreCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Adds a new store branch/dark store for the current vendor."""
    service = VendorService(db)
    vendor = await service.get_by_owner_id(current_user.id)
    if not vendor:
        raise EntityNotFoundError("Vendor profile not found.")
    return await service.add_store(vendor.id, payload)


@router.get("/me/payouts", response_model=List[VendorPayoutResponse])
async def list_my_payouts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists financial settlements and payout history for current vendor."""
    service = VendorService(db)
    vendor = await service.get_by_owner_id(current_user.id)
    if not vendor:
        return []
    return await service.list_payouts(vendor.id)
