"""Payment transaction database repository layer."""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.payments.models import PaymentTransaction, PaymentRefund


class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, payment_id: str) -> Optional[PaymentTransaction]:
        query = select(PaymentTransaction).where(PaymentTransaction.id == payment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_order_id(self, order_id: str) -> Optional[PaymentTransaction]:
        query = select(PaymentTransaction).where(PaymentTransaction.order_id == order_id).order_by(PaymentTransaction.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[PaymentTransaction]:
        query = select(PaymentTransaction).where(PaymentTransaction.idempotency_key == idempotency_key)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_transaction(
        self,
        order_id: str,
        user_id: str,
        amount: float,
        payment_method: str,
        gateway_provider: str = "MOCK_GATEWAY",
        idempotency_key: Optional[str] = None,
    ) -> PaymentTransaction:
        txn = PaymentTransaction(
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            currency="INR",
            payment_method=payment_method,
            gateway_provider=gateway_provider,
            status="PENDING",
            idempotency_key=idempotency_key,
        )
        self.db.add(txn)
        await self.db.flush()
        return txn

    async def update_status(
        self, txn: PaymentTransaction, status: str, gateway_txn_id: Optional[str] = None, error: Optional[str] = None
    ) -> PaymentTransaction:
        txn.status = status
        if gateway_txn_id:
            txn.gateway_txn_id = gateway_txn_id
        if error:
            txn.error_message = error
        await self.db.flush()
        return txn

    async def create_refund(self, payment_id: str, order_id: str, amount: float, reason: str) -> PaymentRefund:
        import uuid
        refund = PaymentRefund(
            payment_id=payment_id,
            order_id=order_id,
            amount=amount,
            reason=reason,
            refund_status="PROCESSED",
            refund_txn_id=f"REF-{uuid.uuid4().hex[:12].upper()}",
        )
        self.db.add(refund)
        await self.db.flush()
        return refund
