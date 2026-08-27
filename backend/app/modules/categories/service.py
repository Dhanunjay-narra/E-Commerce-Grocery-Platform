"""Category service layer for hierarchy resolution and catalog navigation."""
import re
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ConflictError, ValidationError
from app.modules.categories.models import Category
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse
from app.modules.categories.repository import CategoryRepository


def slugify(text: str) -> str:
    """Utility to generate clean URL slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(db)

    async def get_tree(self) -> List[CategoryTreeResponse]:
        """Builds in-memory category tree from a single flat query to prevent async greenlet IO issues."""
        all_cats = await self.repo.list_all(only_active=True)
        
        # Build lookup map of id -> CategoryTreeResponse
        nodes: Dict[str, CategoryTreeResponse] = {}
        for c in all_cats:
            nodes[c.id] = CategoryTreeResponse(
                id=c.id,
                name=c.name,
                slug=c.slug,
                description=c.description,
                parent_id=c.parent_id,
                level=c.level,
                image_url=c.image_url,
                banner_url=c.banner_url,
                icon_name=c.icon_name,
                is_featured=c.is_featured,
                is_active=c.is_active,
                sort_order=c.sort_order,
                created_at=c.created_at,
                subcategories=[],
            )

        root_trees: List[CategoryTreeResponse] = []
        for c in all_cats:
            node = nodes[c.id]
            if c.parent_id and c.parent_id in nodes:
                nodes[c.parent_id].subcategories.append(node)
            elif not c.parent_id:
                root_trees.append(node)

        # Sort subcategories by sort_order
        for node in nodes.values():
            node.subcategories.sort(key=lambda x: (x.sort_order, x.name))

        root_trees.sort(key=lambda x: (x.sort_order, x.name))
        return root_trees

    async def list_all(self) -> List[CategoryResponse]:
        cats = await self.repo.list_all()
        return [CategoryResponse.model_validate(c) for c in cats]

    async def list_featured(self) -> List[CategoryResponse]:
        cats = await self.repo.list_featured()
        return [CategoryResponse.model_validate(c) for c in cats]

    async def get_by_slug(self, slug: str) -> CategoryResponse:
        cat = await self.repo.get_by_slug(slug)
        if not cat:
            raise EntityNotFoundError(f"Category with slug '{slug}' not found.")
        return CategoryResponse.model_validate(cat)

    async def get_by_id(self, category_id: str) -> CategoryResponse:
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise EntityNotFoundError("Category not found.")
        return CategoryResponse.model_validate(cat)

    async def create(self, payload: CategoryCreate) -> CategoryResponse:
        slug = payload.slug or slugify(payload.name)
        existing = await self.repo.get_by_slug(slug)
        if existing:
            import time
            slug = f"{slug}-{int(time.time())}"

        level = 0
        if payload.parent_id:
            parent = await self.repo.get_by_id(payload.parent_id)
            if not parent:
                raise ValidationError("Specified parent category does not exist.")
            level = parent.level + 1
            if level > 2:
                raise ValidationError("Category hierarchy cannot exceed 3 levels (Department -> Category -> Subcategory).")

        cat = await self.repo.create(payload, slug=slug, level=level)
        return CategoryResponse.model_validate(cat)

    async def update(self, category_id: str, payload: CategoryUpdate) -> CategoryResponse:
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise EntityNotFoundError("Category not found.")

        if payload.parent_id and payload.parent_id == category_id:
            raise ValidationError("A category cannot be its own parent.")

        if payload.slug:
            existing = await self.repo.get_by_slug(payload.slug)
            if existing and existing.id != category_id:
                raise ConflictError("A category with this slug already exists.")

        updated = await self.repo.update(cat, payload)
        return CategoryResponse.model_validate(updated)

    async def delete(self, category_id: str) -> None:
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise EntityNotFoundError("Category not found.")
        await self.repo.delete(cat)
