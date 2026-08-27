"""Automated Produce Scale Weight Dispute and Customer Refund State Machine."""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class DisputeStage(str, Enum):
    OPEN = "OPEN"
    EVALUATING_EVIDENCE = "EVALUATING_EVIDENCE"
    AUTO_REFUND_APPROVED = "AUTO_REFUND_APPROVED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"

class WeightDisputeInput(BaseModel):
    ticket_id: str
    order_id: str
    product_sku: str
    charged_scale_weight_kg: float
    customer_claimed_weight_kg: float
    unit_price: float

class DisputeResolution(BaseModel):
    stage: DisputeStage
    variance_pct: float
    refund_amount: float
    resolution_notes: str

class DisputeFSM:
    """Evaluates scale weight discrepancy against dark-store tare calibrations."""

    MAX_AUTO_REFUND_LIMIT = 500.0  # Max ₹500 instant refund without human intervention

    @classmethod
    def resolve_weight_dispute(cls, inp: WeightDisputeInput) -> DisputeResolution:
        charged = inp.charged_scale_weight_kg
        claimed = inp.customer_claimed_weight_kg

        if charged <= 0:
            return DisputeResolution(stage=DisputeStage.REJECTED, variance_pct=0.0, refund_amount=0.0, resolution_notes="Invalid charged weight")

        diff = charged - claimed
        variance_pct = round((diff / charged) * 100.0, 2)

        if diff <= 0:
            return DisputeResolution(
                stage=DisputeStage.REJECTED,
                variance_pct=variance_pct,
                refund_amount=0.0,
                resolution_notes="Delivered weight equal or exceeds claimed weight",
            )

        refund_amt = round(diff * inp.unit_price, 2)

        if refund_amt <= cls.MAX_AUTO_REFUND_LIMIT:
            return DisputeResolution(
                stage=DisputeStage.AUTO_REFUND_APPROVED,
                variance_pct=variance_pct,
                refund_amount=refund_amt,
                resolution_notes=f"Auto-approved instant refund of ₹{refund_amt:.2f} to original payment method",
            )
        else:
            return DisputeResolution(
                stage=DisputeStage.MANUAL_REVIEW_REQUIRED,
                variance_pct=variance_pct,
                refund_amount=refund_amt,
                resolution_notes="High value variance queued for Dark Store Lead physical verification",
            )
