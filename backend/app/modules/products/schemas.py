"""Pydantic schemas for master product catalog, variable weight pricing, images, and variants."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductImageCreate(BaseModel):
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    sort_order: int = 0


class ProductImageResponse(BaseModel):
    id: str
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


class ProductVariantCreate(BaseModel):
    sku: str
    title: str
    price_override: Optional[float] = None
    attributes: Optional[str] = None


class ProductVariantResponse(BaseModel):
    id: str
    sku: str
    title: str
    price_override: Optional[float] = None
    attributes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=64)
    barcode: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=200)
    slug: Optional[str] = None
    brand: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category_id: str
    unit: str = Field(default="pcs", description="kg, g, L, ml, pcs, bunch, pack")
    base_price: float = Field(..., gt=0)
    sale_price: float = Field(..., gt=0)
    cost_price: float = Field(default=0.0, ge=0)
    tax_rate: float = Field(default=0.0, ge=0, le=100)
    is_variable_weight: bool = False
    weight_increment: float = 1.0
    weight_tolerance_pct: float = 15.0
    min_order_qty: float = 1.0
    max_order_qty: float = 50.0
    ingredients: Optional[str] = None
    nutritional_info: Optional[str] = None
    allergen_info: Optional[str] = None
    storage_instructions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    country_of_origin: str = "India"
    manufacturer: Optional[str] = None
    is_organic: bool = False
    is_vegetarian: bool = True
    is_vegan: bool = False
    is_gluten_free: bool = False
    is_diabetic_friendly: bool = False
    status: str = "ACTIVE"
    images: Optional[List[ProductImageCreate]] = None
    variants: Optional[List[ProductVariantCreate]] = None


class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    unit: Optional[str] = None
    base_price: Optional[float] = Field(None, gt=0)
    sale_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, ge=0)
    tax_rate: Optional[float] = Field(None, ge=0, le=100)
    is_variable_weight: Optional[bool] = None
    weight_increment: Optional[float] = None
    weight_tolerance_pct: Optional[float] = None
    min_order_qty: Optional[float] = None
    max_order_qty: Optional[float] = None
    ingredients: Optional[str] = None
    nutritional_info: Optional[str] = None
    allergen_info: Optional[str] = None
    storage_instructions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    country_of_origin: Optional[str] = None
    manufacturer: Optional[str] = None
    is_organic: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_diabetic_friendly: Optional[bool] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    sku: str
    barcode: Optional[str] = None
    name: str
    slug: str
    brand: str
    description: Optional[str] = None
    category_id: str
    unit: str
    base_price: float
    sale_price: float
    tax_rate: float
    is_variable_weight: bool
    weight_increment: float
    weight_tolerance_pct: float
    min_order_qty: float
    max_order_qty: float
    is_organic: bool
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    is_diabetic_friendly: bool
    status: str
    rating_average: float
    rating_count: int
    primary_image_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(ProductResponse):
    ingredients: Optional[str] = None
    nutritional_info: Optional[str] = None
    allergen_info: Optional[str] = None
    storage_instructions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    country_of_origin: str
    manufacturer: Optional[str] = None
    images: List[ProductImageResponse] = []
    variants: List[ProductVariantResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Variable Weight Pricing Calculation Models
class VariableWeightPricingCalcRequest(BaseModel):
    requested_qty: float = Field(..., gt=0, description="Quantity customer ordered, e.g. 1.0 kg")
    actual_picked_qty: float = Field(..., gt=0, description="Exact scale weight measured by picker, e.g. 1.08 kg")


class VariableWeightPricingCalcResponse(BaseModel):
    product_id: str
    unit: str
    unit_sale_price: float
    requested_qty: float
    estimated_price: float
    actual_picked_qty: float
    final_reconciled_price: float
    price_delta: float
    is_within_tolerance: bool
    tolerance_pct_applied: float
