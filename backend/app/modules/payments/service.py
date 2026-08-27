"""Payment gateway abstraction and verification service."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, PaymentError, ValidationError
from app.modules.payments.models import PaymentTransaction, PaymentRefund
from app.modules.payments.schemas import (
    PaymentInitiateRequest,
    PaymentInitiateResponse,
    PaymentVerifyRequest,
    PaymentResponse,
    RefundRequest,
    RefundResponse,
)
from app.modules.payments.repository import PaymentRepository


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PaymentRepository(db)

    async def initiate_payment(self, payload: PaymentInitiateRequest, user_id: str) -> PaymentInitiateResponse:
        if payload.idempotency_key:
            existing = await self.repo.get_by_idempotency_key(payload.idempotency_key)
            if existing:
                return PaymentInitiateResponse(
                    transaction_id=existing.id,
                    order_id=existing.order_id,
                    amount=existing.amount,
                    currency=existing.currency,
                    payment_method=existing.payment_method,
                    gateway_provider=existing.gateway_provider,
                    status=existing.status,
                    message="Retrieved existing idempotent payment transaction.",
                )

        txn = await self.repo.create_transaction(
            order_id=payload.order_id,
            user_id=user_id,
            amount=payload.amount,
            payment_method=payload.payment_method,
            gateway_provider=payload.gateway_provider,
            idempotency_key=payload.idempotency_key,
        )

        # In Cash-on-Delivery, auto-authorize immediately
        if payload.payment_method == "CASH_ON_DELIVERY":
            await self.repo.update_status(txn, "AUTHORIZED", gateway_txn_id=f"COD-{uuid.uuid4().hex[:8].upper()}")

        return PaymentInitiateResponse(
            transaction_id=txn.id,
            order_id=txn.order_id,
            amount=txn.amount,
            currency=txn.currency,
            payment_method=txn.payment_method,
            gateway_provider=txn.gateway_provider,
            client_secret=f"mock_secret_{txn.id}",
            status=txn.status,
            message="Payment initiated. Ready for authorization.",
        )

    async def verify_payment(self, payload: PaymentVerifyRequest) -> PaymentResponse:
        txn = await self.repo.get_by_id(payload.transaction_id)
        if not txn:
            raise EntityNotFoundError("Payment transaction not found.")

        if not payload.simulate_success:
            await self.repo.update_status(txn, "FAILED", error="Card declined / Insufficient funds")
            raise PaymentError("Payment transaction was declined by the bank.")

        gateway_ref = payload.gateway_txn_id or f"GTW-TXN-{uuid.uuid4().hex[:12].upper()}"
        updated_txn = await self.repo.update_status(txn, "CAPTURED", gateway_txn_id=gateway_ref)
        return PaymentResponse.model_validate(updated_txn)

    async def refund_payment(self, payload: RefundRequest) -> RefundResponse:
        txn = await self.repo.get_by_id(payload.payment_id)
        if not txn:
            raise EntityNotFoundError("Payment transaction not found.")

        if txn.status not in ["CAPTURED", "AUTHORIZED"]:
            raise ValidationError(f"Cannot refund a payment with status '{txn.status}'.")

        refund = await self.repo.create_refund(txn.id, txn.order_id, payload.amount, payload.reason)
        await self.repo.update_status(txn, "REFUNDED")

        return RefundResponse(
            refund_id=refund.id,
            payment_id=txn.id,
            amount=refund.amount,
            refund_status="PROCESSED",
            message="Refund processed successfully back to payment source.",
        )
