"""Pydantic schemas for search query parsing, suggestions, and faceted results."""
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from app.modules.products.schemas import ProductResponse


class SearchFacetItem(BaseModel):
    label: str
    value: str
    count: int


class SearchFacets(BaseModel):
    categories: List[SearchFacetItem] = []
    brands: List[SearchFacetItem] = []
    dietary: Dict[str, int] = {}
    price_ranges: List[SearchFacetItem] = []


class SearchResponse(BaseModel):
    query: str
    corrected_query: Optional[str] = None
    items: List[ProductResponse] = []
    total: int
    facets: SearchFacets
    detected_intents: List[str] = []


class SearchSuggestion(BaseModel):
    text: str
    category: Optional[str] = None
    product_id: Optional[str] = None
    type: str = "query"  # "query", "product", "category", "brand"


class PopularSearch(BaseModel):
    keyword: str
    search_count: int
