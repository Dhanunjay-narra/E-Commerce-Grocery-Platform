"""Product Catalog database repository layer."""
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.products.models import Product, ProductImage, ProductVariant
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductImageCreate, ProductVariantCreate


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        query = (
            select(Product)
            .where(and_(Product.id == product_id, Product.is_deleted == False))
            .options(
                selectinload(Product.images),
                selectinload(Product.variants),
                selectinload(Product.category),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_or_slug(self, identifier: str) -> Optional[Product]:
        query = (
            select(Product)
            .where(
                and_(
                    or_(Product.id == identifier, Product.slug == identifier.lower().strip()),
                    Product.is_deleted == False,
                )
            )
            .options(
                selectinload(Product.images),
                selectinload(Product.variants),
                selectinload(Product.category),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        query = select(Product).where(and_(Product.sku == sku.upper().strip(), Product.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        query = (
            select(Product)
            .where(and_(Product.barcode == barcode.strip(), Product.is_deleted == False))
            .options(
                selectinload(Product.images),
                selectinload(Product.variants),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_products(
        self,
        category_id: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_organic: Optional[bool] = None,
        is_vegan: Optional[bool] = None,
        is_vegetarian: Optional[bool] = None,
        is_gluten_free: Optional[bool] = None,
        status: Optional[str] = "ACTIVE",
        sort_by: Optional[str] = "newest",  # newest, price_low, price_high, rating
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Product], int]:
        conditions = [Product.is_deleted == False]
        if status:
            conditions.append(Product.status == status)
        if category_id:
            conditions.append(Product.category_id == category_id)
        if brand:
            conditions.append(Product.brand.ilike(f"%{brand}%"))
        if min_price is not None:
            conditions.append(Product.sale_price >= min_price)
        if max_price is not None:
            conditions.append(Product.sale_price <= max_price)
        if is_organic is not None:
            conditions.append(Product.is_organic == is_organic)
        if is_vegan is not None:
            conditions.append(Product.is_vegan == is_vegan)
        if is_vegetarian is not None:
            conditions.append(Product.is_vegetarian == is_vegetarian)
        if is_gluten_free is not None:
            conditions.append(Product.is_gluten_free == is_gluten_free)

        # Count total
        count_query = select(func.count(Product.id)).where(and_(*conditions))
        total_count = (await self.db.execute(count_query)).scalar() or 0

        # Query items
        query = (
            select(Product)
            .where(and_(*conditions))
            .options(selectinload(Product.images))
        )

        if sort_by == "price_low":
            query = query.order_by(Product.sale_price.asc())
        elif sort_by == "price_high":
            query = query.order_by(Product.sale_price.desc())
        elif sort_by == "rating":
            query = query.order_by(Product.rating_average.desc())
        else:
            query = query.order_by(Product.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total_count

    async def create(self, payload: ProductCreate, slug: str) -> Product:
        product = Product(
            sku=payload.sku.upper().strip(),
            barcode=payload.barcode,
            name=payload.name,
            slug=slug,
            brand=payload.brand,
            description=payload.description,
            category_id=payload.category_id,
            unit=payload.unit,
            base_price=payload.base_price,
            sale_price=payload.sale_price,
            cost_price=payload.cost_price,
            tax_rate=payload.tax_rate,
            is_variable_weight=payload.is_variable_weight,
            weight_increment=payload.weight_increment,
            weight_tolerance_pct=payload.weight_tolerance_pct,
            min_order_qty=payload.min_order_qty,
            max_order_qty=payload.max_order_qty,
            ingredients=payload.ingredients,
            nutritional_info=payload.nutritional_info,
            allergen_info=payload.allergen_info,
            storage_instructions=payload.storage_instructions,
            shelf_life_days=payload.shelf_life_days,
            country_of_origin=payload.country_of_origin,
            manufacturer=payload.manufacturer,
            is_organic=payload.is_organic,
            is_vegetarian=payload.is_vegetarian,
            is_vegan=payload.is_vegan,
            is_gluten_free=payload.is_gluten_free,
            is_diabetic_friendly=payload.is_diabetic_friendly,
            status=payload.status,
        )
        self.db.add(product)
        await self.db.flush()

        if payload.images:
            for img in payload.images:
                db_img = ProductImage(
                    product_id=product.id,
                    image_url=img.image_url,
                    alt_text=img.alt_text,
                    is_primary=img.is_primary,
                    sort_order=img.sort_order,
                )
                self.db.add(db_img)

        if payload.variants:
            for var in payload.variants:
                db_var = ProductVariant(
                    product_id=product.id,
                    sku=var.sku.upper().strip(),
                    title=var.title,
                    price_override=var.price_override,
                    attributes=var.attributes,
                )
                self.db.add(db_var)

        await self.db.flush()
        return await self.get_by_id(product.id)  # type: ignore

    async def update(self, product: Product, payload: ProductUpdate) -> Product:
        update_data = payload.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(product, field, val)
        await self.db.flush()
        return await self.get_by_id(product.id)  # type: ignore

    async def delete(self, product: Product) -> None:
        product.soft_delete()
        await self.db.flush()
