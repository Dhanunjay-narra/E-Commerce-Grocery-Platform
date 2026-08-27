"""Pydantic schemas for FEFO inventory batches, warehouses, and reservations."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=30)
    type: str = "DARK_STORE"  # CENTRAL_WAREHOUSE, DARK_STORE, VENDOR_STORE
    address: str
    city: str
    latitude: float
    longitude: float


class WarehouseResponse(BaseModel):
    id: str
    name: str
    code: str
    type: str
    address: str
    city: str
    latitude: float
    longitude: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class InventoryBatchCreate(BaseModel):
    batch_number: str = Field(..., min_length=2, max_length=64)
    product_id: str
    vendor_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    expiry_date: datetime
    procurement_cost: float = Field(default=0.0, ge=0)
    initial_qty: float = Field(..., gt=0)


class InventoryBatchUpdate(BaseModel):
    available_qty: Optional[float] = None
    damaged_qty: Optional[float] = None
    status: Optional[str] = None


class InventoryBatchResponse(BaseModel):
    id: str
    batch_number: str
    product_id: str
    vendor_id: Optional[str] = None
    warehouse_id: Optional[str] = None
    manufacturing_date: Optional[datetime] = None
    expiry_date: datetime
    procurement_cost: float
    initial_qty: float
    available_qty: float
    reserved_qty: float
    damaged_qty: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# FEFO Allocation Schemas
class FEFOAllocationItem(BaseModel):
    batch_id: str
    batch_number: str
    expiry_date: datetime
    allocated_qty: float
    procurement_cost: float


class FEFOAllocationRequest(BaseModel):
    product_id: str
    requested_qty: float = Field(..., gt=0)
    vendor_id: Optional[str] = None


class FEFOAllocationResponse(BaseModel):
    product_id: str
    requested_qty: float
    total_allocated_qty: float
    is_fully_allocated: bool
    allocations: List[FEFOAllocationItem] = []


class StockReservationRequest(BaseModel):
    reference_id: str = Field(..., description="Cart ID or Order ID")
    product_id: str
    quantity: float = Field(..., gt=0)
    vendor_id: Optional[str] = None
    ttl_seconds: int = Field(default=600, description="10-minute hold lock")


class StockReservationResponse(BaseModel):
    reference_id: str
    product_id: str
    reserved_qty: float
    expires_at: datetime
    is_successful: bool
    reservations: List[FEFOAllocationItem] = []


class StockReleaseRequest(BaseModel):
    reference_id: str


class InventoryAdjustRequest(BaseModel):
    batch_id: str
    quantity_delta: float = Field(..., description="Positive for addition, negative for reduction/damage")
    reason: str = Field(..., description="RECEIPT, DAMAGE, EXPIRED_WASTE, AUDIT_CORRECTION")
    reference_id: Optional[str] = None


class LowStockAlertResponse(BaseModel):
    product_id: str
    product_name: str
    sku: str
    total_available_qty: float
    threshold: float
    nearest_expiry_date: Optional[datetime] = None
