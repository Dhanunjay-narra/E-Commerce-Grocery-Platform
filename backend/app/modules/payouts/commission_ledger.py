"""Double-Entry Vendor Payout Ledger and TDS Tax Withholding Engine."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

class LedgerEntry(BaseModel):
    entry_id: str
    vendor_id: str
    order_id: str
    gross_order_amount: float
    platform_commission_pct: float
    platform_commission_amount: float
    tds_withheld_amount: float  # 1% TDS under Section 194-O
    gst_on_commission_amount: float  # 18% GST on platform commission
    net_vendor_payable_amount: float
    created_at: datetime

class VendorPayoutLedgerEngine:
    """Calculates exact statutory TDS deductions, GST invoices, and net vendor bank settlement batches."""

    TDS_SECTION_194O_RATE = 1.0   # 1% TDS on e-commerce gross sales
    GST_ON_SERVICE_RATE = 18.0     # 18% GST on marketplace commission

    @classmethod
    def calculate_order_split(
        cls,
        entry_id: str,
        vendor_id: str,
        order_id: str,
        gross_amount: float,
        commission_rate_pct: float = 8.5,
    ) -> LedgerEntry:
        gross = round(gross_amount, 2)
        comm = round((gross * commission_rate_pct) / 100.0, 2)
        gst_on_comm = round((comm * cls.GST_ON_SERVICE_RATE) / 100.0, 2)
        tds = round((gross * cls.TDS_SECTION_194O_RATE) / 100.0, 2)
        
        # Net Payable = Gross - Commission - GST on Commission - TDS
        net_payable = round(gross - comm - gst_on_comm - tds, 2)

        return LedgerEntry(
            entry_id=entry_id,
            vendor_id=vendor_id,
            order_id=order_id,
            gross_order_amount=gross,
            platform_commission_pct=commission_rate_pct,
            platform_commission_amount=comm,
            tds_withheld_amount=tds,
            gst_on_commission_amount=gst_on_comm,
            net_vendor_payable_amount=net_payable,
            created_at=datetime.now(timezone.utc),
        )
