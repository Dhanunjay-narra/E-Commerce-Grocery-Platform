"""Executive Business Intelligence, Aggregation Metrics, and Compliance Audit service."""
import json
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.admin.models import AuditLog
from app.modules.admin.schemas import (
    AuditLogResponse,
    ExecutiveDashboardMetricsResponse,
    CategorySalesMetric,
)
from app.modules.orders.models import Order, OrderItem
from app.modules.users.models import User
from app.modules.vendors.models import Vendor
from app.modules.categories.models import Category
from app.modules.products.models import Product


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        actor_id: str,
        actor_email: str,
        actor_role: str,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Records an immutable administrative audit record."""
        changes_str = json.dumps(changes) if changes else None
        log = AuditLog(
            actor_id=actor_id,
            actor_email=actor_email,
            actor_role=actor_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes_json=changes_str,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_audit_logs(self, limit: int = 50) -> List[AuditLogResponse]:
        query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())
        return [AuditLogResponse.model_validate(l) for l in logs]

    async def get_dashboard_metrics(self) -> ExecutiveDashboardMetricsResponse:
        """Aggregates enterprise KPIs across orders, vendors, users, and categories."""
        # 1. Total Orders & GMV
        orders_query = select(
            func.count(Order.id),
            func.sum(Order.grand_total),
        ).where(Order.status != "CANCELLED")
        orders_res = await self.db.execute(orders_query)
        tot_orders, gmv = orders_res.one()
        tot_orders = tot_orders or 0
        gmv = float(gmv or 0.0)

        # 2. Completed Orders
        comp_query = select(func.count(Order.id)).where(Order.status == "DELIVERED")
        comp_res = await self.db.execute(comp_query)
        comp_orders = comp_res.scalar() or 0

        # 3. Active Customers & Vendors
        cust_query = select(func.count(User.id)).where(User.is_active == True)
        cust_res = await self.db.execute(cust_query)
        active_customers = cust_res.scalar() or 0

        vend_query = select(func.count(Vendor.id)).where(and_(Vendor.kyc_status == "APPROVED", Vendor.is_active == True))
        vend_res = await self.db.execute(vend_query)
        active_vendors = vend_res.scalar() or 0

        # 4. AOV & Return Rate
        aov = round(gmv / tot_orders, 2) if tot_orders > 0 else 0.0

        returned_query = select(func.count(Order.id)).where(Order.status.in_(["RETURNED", "REFUNDED"]))
        ret_res = await self.db.execute(returned_query)
        ret_orders = ret_res.scalar() or 0
        return_rate = round((ret_orders / tot_orders * 100.0), 2) if tot_orders > 0 else 0.0

        # 5. Top Categories Breakdown
        cat_query = (
            select(
                Product.category_id,
                func.sum(OrderItem.item_subtotal).label("revenue"),
                func.sum(OrderItem.ordered_qty).label("units"),
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .group_by(Product.category_id)
            .order_by(func.sum(OrderItem.item_subtotal).desc())
            .limit(5)
        )
        cat_res = await self.db.execute(cat_query)
        top_cats = []
        for r in cat_res.all():
            cat = await self.db.get(Category, r[0])
            cat_name = cat.name if cat else "Uncategorized"
            top_cats.append(
                CategorySalesMetric(
                    category_id=r[0],
                    category_name=cat_name,
                    revenue=round(float(r[1] or 0.0), 2),
                    units_sold=round(float(r[2] or 0.0), 2),
                )
            )

        return ExecutiveDashboardMetricsResponse(
            gross_merchandise_value=round(gmv, 2),
            total_orders_count=tot_orders,
            completed_orders_count=comp_orders,
            active_customers_count=active_customers,
            active_vendors_count=active_vendors,
            average_order_value=aov,
            return_rate_percentage=return_rate,
            top_categories=top_cats,
        )
