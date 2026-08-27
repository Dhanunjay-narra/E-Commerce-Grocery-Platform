"""Pydantic schemas for Executive Analytics, Dashboard Metrics, and Audit Logs."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str
    actor_email: str
    actor_role: str
    action: str
    entity_type: str
    entity_id: str
    changes_json: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategorySalesMetric(BaseModel):
    category_id: str
    category_name: str
    revenue: float
    units_sold: float


class ExecutiveDashboardMetricsResponse(BaseModel):
    gross_merchandise_value: float
    total_orders_count: int
    completed_orders_count: int
    active_customers_count: int
    active_vendors_count: int
    average_order_value: float
    return_rate_percentage: float
    top_categories: List[CategorySalesMetric] = []
