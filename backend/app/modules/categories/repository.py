"""Category database repository."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.categories.models import Category
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: str) -> Optional[Category]:
        query = select(Category).where(and_(Category.id == category_id, Category.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        query = (
            select(Category)
            .where(and_(Category.slug == slug.lower().strip(), Category.is_deleted == False))
            .options(selectinload(Category.subcategories))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all(self, only_active: bool = True) -> List[Category]:
        query = select(Category).where(Category.is_deleted == False)
        if only_active:
            query = query.where(Category.is_active == True)
        query = query.order_by(Category.level.asc(), Category.sort_order.asc(), Category.name.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_featured(self) -> List[Category]:
        query = (
            select(Category)
            .where(and_(Category.is_featured == True, Category.is_active == True, Category.is_deleted == False))
            .order_by(Category.sort_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_root_departments(self) -> List[Category]:
        query = (
            select(Category)
            .where(and_(Category.parent_id == None, Category.is_active == True, Category.is_deleted == False))
            .options(
                selectinload(Category.subcategories).selectinload(Category.subcategories)
            )
            .order_by(Category.sort_order.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, payload: CategoryCreate, slug: str, level: int = 0) -> Category:
        category = Category(
            name=payload.name,
            slug=slug,
            description=payload.description,
            parent_id=payload.parent_id,
            level=level,
            image_url=payload.image_url,
            banner_url=payload.banner_url,
            icon_name=payload.icon_name,
            is_featured=payload.is_featured,
            sort_order=payload.sort_order,
            meta_title=payload.meta_title,
            meta_description=payload.meta_description,
        )
        self.db.add(category)
        await self.db.flush()
        return category

    async def update(self, category: Category, payload: CategoryUpdate) -> Category:
        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(category, field, val)
        await self.db.flush()
        return category

    async def delete(self, category: Category) -> None:
        category.soft_delete()
        await self.db.flush()
