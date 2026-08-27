"""Product domain business logic and variable-weight pricing service."""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundError, ConflictError, ValidationError
from app.modules.products.models import Product
from app.modules.products.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDetailResponse,
    ProductImageResponse,
    ProductVariantResponse,
    VariableWeightPricingCalcRequest,
    VariableWeightPricingCalcResponse,
)
from app.modules.products.repository import ProductRepository
from app.modules.categories.repository import CategoryRepository
from app.modules.categories.service import slugify


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)
        self.cat_repo = CategoryRepository(db)

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
        sort_by: Optional[str] = "newest",
        skip: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        items, total = await self.repo.list_products(
            category_id=category_id,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            is_organic=is_organic,
            is_vegan=is_vegan,
            is_vegetarian=is_vegetarian,
            is_gluten_free=is_gluten_free,
            status=status,
            sort_by=sort_by,
            skip=skip,
            limit=limit,
        )

        dtos = []
        for p in items:
            primary_img = next((img.image_url for img in p.images if img.is_primary), None)
            if not primary_img and p.images:
                primary_img = p.images[0].image_url

            dto = ProductResponse(
                id=p.id,
                sku=p.sku,
                barcode=p.barcode,
                name=p.name,
                slug=p.slug,
                brand=p.brand,
                description=p.description,
                category_id=p.category_id,
                unit=p.unit,
                base_price=p.base_price,
                sale_price=p.sale_price,
                tax_rate=p.tax_rate,
                is_variable_weight=p.is_variable_weight,
                weight_increment=p.weight_increment,
                weight_tolerance_pct=p.weight_tolerance_pct,
                min_order_qty=p.min_order_qty,
                max_order_qty=p.max_order_qty,
                is_organic=p.is_organic,
                is_vegetarian=p.is_vegetarian,
                is_vegan=p.is_vegan,
                is_gluten_free=p.is_gluten_free,
                is_diabetic_friendly=p.is_diabetic_friendly,
                status=p.status,
                rating_average=p.rating_average,
                rating_count=p.rating_count,
                primary_image_url=primary_img,
                created_at=p.created_at,
            )
            dtos.append(dto)

        return {"items": dtos, "total": total, "skip": skip, "limit": limit}

    async def get_by_id_or_slug(self, identifier: str) -> ProductDetailResponse:
        product = await self.repo.get_by_id_or_slug(identifier)
        if not product:
            raise EntityNotFoundError(f"Product '{identifier}' not found.")
        return self._map_detail_dto(product)

    async def get_by_barcode(self, barcode: str) -> ProductDetailResponse:
        product = await self.repo.get_by_barcode(barcode)
        if not product:
            raise EntityNotFoundError(f"Product with barcode '{barcode}' not found.")
        return self._map_detail_dto(product)

    async def create(self, payload: ProductCreate) -> ProductDetailResponse:
        # Check SKU uniqueness
        existing_sku = await self.repo.get_by_sku(payload.sku)
        if existing_sku:
            raise ConflictError(f"A product with SKU '{payload.sku}' already exists.")

        # Check Category exists
        category = await self.cat_repo.get_by_id(payload.category_id)
        if not category:
            raise ValidationError("Specified category does not exist.")

        slug = payload.slug or slugify(f"{payload.brand}-{payload.name}")
        existing_slug = await self.repo.get_by_id_or_slug(slug)
        if existing_slug:
            slug = f"{slug}-{payload.sku.lower()}"

        product = await self.repo.create(payload, slug=slug)
        return self._map_detail_dto(product)

    async def update(self, product_id: str, payload: ProductUpdate) -> ProductDetailResponse:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise EntityNotFoundError("Product not found.")

        if payload.category_id:
            category = await self.cat_repo.get_by_id(payload.category_id)
            if not category:
                raise ValidationError("Specified category does not exist.")

        updated = await self.repo.update(product, payload)
        return self._map_detail_dto(updated)

    async def delete(self, product_id: str) -> None:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise EntityNotFoundError("Product not found.")
        await self.repo.delete(product)

    async def calculate_variable_weight_pricing(
        self, product_id: str, payload: VariableWeightPricingCalcRequest
    ) -> VariableWeightPricingCalcResponse:
        """Calculates variable-weight estimated vs actual price reconciliation and tolerance checks."""
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise EntityNotFoundError("Product not found.")

        unit_price = product.sale_price
        estimated_price = round(unit_price * payload.requested_qty, 2)
        actual_price = round(unit_price * payload.actual_picked_qty, 2)
        delta_amount = round(actual_price - estimated_price, 2)

        # Check tolerance percentage: |actual - requested| / requested * 100
        qty_variance_pct = abs(payload.actual_picked_qty - payload.requested_qty) / payload.requested_qty * 100.0
        is_within_tolerance = qty_variance_pct <= product.weight_tolerance_pct

        return VariableWeightPricingCalcResponse(
            product_id=product.id,
            unit=product.unit,
            unit_sale_price=unit_price,
            requested_qty=payload.requested_qty,
            estimated_price=estimated_price,
            actual_picked_qty=payload.actual_picked_qty,
            final_reconciled_price=actual_price,
            price_delta=delta_amount,
            is_within_tolerance=is_within_tolerance,
            tolerance_pct_applied=product.weight_tolerance_pct,
        )

    def _map_detail_dto(self, p: Product) -> ProductDetailResponse:
        primary_img = next((img.image_url for img in p.images if img.is_primary), None)
        if not primary_img and p.images:
            primary_img = p.images[0].image_url

        images_dto = [ProductImageResponse.model_validate(img) for img in p.images]
        variants_dto = [ProductVariantResponse.model_validate(v) for v in p.variants]

        return ProductDetailResponse(
            id=p.id,
            sku=p.sku,
            barcode=p.barcode,
            name=p.name,
            slug=p.slug,
            brand=p.brand,
            description=p.description,
            category_id=p.category_id,
            unit=p.unit,
            base_price=p.base_price,
            sale_price=p.sale_price,
            tax_rate=p.tax_rate,
            is_variable_weight=p.is_variable_weight,
            weight_increment=p.weight_increment,
            weight_tolerance_pct=p.weight_tolerance_pct,
            min_order_qty=p.min_order_qty,
            max_order_qty=p.max_order_qty,
            ingredients=p.ingredients,
            nutritional_info=p.nutritional_info,
            allergen_info=p.allergen_info,
            storage_instructions=p.storage_instructions,
            shelf_life_days=p.shelf_life_days,
            country_of_origin=p.country_of_origin,
            manufacturer=p.manufacturer,
            is_organic=p.is_organic,
            is_vegetarian=p.is_vegetarian,
            is_vegan=p.is_vegan,
            is_gluten_free=p.is_gluten_free,
            is_diabetic_friendly=p.is_diabetic_friendly,
            status=p.status,
            rating_average=p.rating_average,
            rating_count=p.rating_count,
            primary_image_url=primary_img,
            created_at=p.created_at,
            images=images_dto,
            variants=variants_dto,
        )
