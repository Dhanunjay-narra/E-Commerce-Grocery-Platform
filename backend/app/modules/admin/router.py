"""Executive Analytics and Audit Trail API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import UserRole
from app.modules.authentication.permissions import require_role
from app.modules.admin.schemas import (
    AuditLogResponse,
    ExecutiveDashboardMetricsResponse,
)
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])


@router.get(
    "/analytics/dashboard",
    response_model=ExecutiveDashboardMetricsResponse,
    dependencies=[Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value))],
)
async def get_executive_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """Real-time enterprise dashboard metrics: GMV, completed orders, active vendors, and category revenue."""
    service = AdminService(db)
    return await service.get_dashboard_metrics()


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value))],
)
async def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves immutable audit records for regulatory compliance and administrative tracking."""
    service = AdminService(db)
    return await service.list_audit_logs(limit=limit)
