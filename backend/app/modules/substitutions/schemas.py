"""Pydantic schemas for Smart Substitutions."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.modules.products.schemas import ProductResponse


class SubstitutionSuggestionItem(BaseModel):
    product: ProductResponse
    match_score: float  # 0.0 to 1.0
    price_delta: float
    reason: str  # "Same Brand & Category", "Best-selling Alternative in Category"


class SubstitutionSuggestResponse(BaseModel):
    original_product_id: str
    suggestions: List[SubstitutionSuggestionItem] = []


class SubstitutionRuleCreate(BaseModel):
    original_product_id: str
    substitute_product_id: str
    priority_score: float = 1.0


class SubstitutionRuleResponse(BaseModel):
    id: str
    original_product_id: str
    substitute_product_id: str
    priority_score: float
    is_approved: bool

    model_config = ConfigDict(from_attributes=True)
