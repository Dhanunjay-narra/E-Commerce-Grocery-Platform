"""Payment Processing and Transaction Verification API endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import get_current_user, require_role
from app.modules.users.models import User
from app.modules.payments.schemas import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentVerifyRequest,
    PaymentResponse,
    RefundRequest,
    RefundResponse,
)
from app.modules.payments.service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initiate", response_model=PaymentInitiateResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    payload: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiates an idempotent payment transaction for an active grocery order."""
    service = PaymentService(db)
    return await service.initiate_payment(payload, user_id=current_user.id)


@router.post("/verify", response_model=PaymentResponse)
async def verify_payment(
    payload: PaymentVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verifies payment gateway callback and captures transaction funds."""
    service = PaymentService(db)
    return await service.verify_payment(payload)


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(
    payload: RefundRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(UserRole.ADMIN.value, UserRole.SUPPORT_AGENT.value, UserRole.SUPER_ADMIN.value)),
):
    """Admin / Support endpoint to issue refunds for cancellations or returns."""
    service = PaymentService(db)
    return await service.refund_payment(payload)
