"""Production-Grade Master Grocery Catalog and Multi-Vendor Logistics Seed Script."""
import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta, date

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import async_session_factory, init_db, engine
from app.core.security import get_password_hash, UserRole
from app.modules.users.models import User, UserAddress
from app.modules.categories.models import Category
from app.modules.products.models import Product, ProductImage, ProductVariant
from app.modules.vendors.models import Vendor, VendorStore
from app.modules.inventory.models import Warehouse, InventoryBatch
from app.modules.coupons.models import Coupon
from app.modules.shipping.models import DeliveryZone, DeliverySlot
from app.modules.substitutions.models import ProductSubstitutionRule


async def seed_master_dataset():
    print("[*] Initializing FreshCart database schema...")
    async with engine.begin() as conn:
        from app.core.database import _import_all_models, Base
        _import_all_models()
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        print("[*] Seeding Users and Administrative Personas...")
        # 1. Users
        super_admin = User(
            email="admin@freshcart.com",
            phone="+919000000001",
            full_name="Executive Administrator",
            hashed_password=get_password_hash("AdminSecure2026!"),
            role=UserRole.SUPER_ADMIN.value,
            is_active=True,
            is_verified=True,
        )
        vendor_owner = User(
            email="vendor@organicfarm.com",
            phone="+919000000002",
            full_name="Vikram Reddy",
            hashed_password=get_password_hash("VendorPass2026!"),
            role=UserRole.VENDOR_OWNER.value,
            is_active=True,
            is_verified=True,
        )
        store_picker = User(
            email="picker@freshcart.com",
            phone="+919000000003",
            full_name="Suresh Picker",
            hashed_password=get_password_hash("PickerPass2026!"),
            role=UserRole.VENDOR_STAFF.value,
            is_active=True,
            is_verified=True,
        )
        delivery_agent = User(
            email="driver@freshcart.com",
            phone="+919000000004",
            full_name="Ramesh Driver",
            hashed_password=get_password_hash("DriverPass2026!"),
            role=UserRole.DELIVERY_AGENT.value,
            is_active=True,
            is_verified=True,
        )
        customer_1 = User(
            email="priya.sharma@gmail.com",
            phone="+919876543210",
            full_name="Priya Sharma",
            hashed_password=get_password_hash("CustomerPass2026!"),
            role=UserRole.CUSTOMER.value,
            is_active=True,
            is_verified=True,
        )
        customer_2 = User(
            email="arun.patel@gmail.com",
            phone="+919876543211",
            full_name="Arun Patel",
            hashed_password=get_password_hash("CustomerPass2026!"),
            role=UserRole.CUSTOMER.value,
            is_active=True,
            is_verified=True,
        )

        session.add_all([super_admin, vendor_owner, store_picker, delivery_agent, customer_1, customer_2])
        await session.flush()

        # Customer Addresses
        addr_1 = UserAddress(
            user_id=customer_1.id,
            label="Home",
            recipient_name="Priya Sharma",
            recipient_phone="+919876543210",
            street_address="Flat 402, Green Valley Apartments, Hitec City",
            city="Hyderabad",
            state="Telangana",
            postal_code="500081",
            latitude=17.4435,
            longitude=78.3772,
            is_default=True,
        )
        session.add(addr_1)

        print("[*] Seeding 3-Tier Category Taxonomy...")
        # 2. Departments & Categories
        dept_produce = Category(name="Fresh Produce", slug="fresh-produce", level=0, sort_order=1)
        dept_dairy = Category(name="Dairy & Bakery", slug="dairy-bakery", level=0, sort_order=2)
        dept_pantry = Category(name="Pantry Staples", slug="pantry-staples", level=0, sort_order=3)
        dept_beverages = Category(name="Beverages & Snacks", slug="beverages-snacks", level=0, sort_order=4)
        session.add_all([dept_produce, dept_dairy, dept_pantry, dept_beverages])
        await session.flush()

        # Tier-1 Categories
        cat_fruits = Category(name="Fresh Fruits", slug="fresh-fruits", parent_id=dept_produce.id, level=1)
        cat_veggies = Category(name="Fresh Vegetables", slug="fresh-vegetables", parent_id=dept_produce.id, level=1)
        cat_milk = Category(name="Milk & Butter", slug="milk-butter", parent_id=dept_dairy.id, level=1)
        cat_oils = Category(name="Cooking Oils & Ghee", slug="cooking-oils-ghee", parent_id=dept_pantry.id, level=1)
        cat_rice = Category(name="Rice & Grains", slug="rice-grains", parent_id=dept_pantry.id, level=1)
        session.add_all([cat_fruits, cat_veggies, cat_milk, cat_oils, cat_rice])
        await session.flush()

        print("[*] Seeding Master Product Catalog with Dietary & Variable-Weight Metadata...")
        # 3. Master Products
        # Tomatoes (Variable weight)
        p_tomatoes = Product(
            sku="PROD-TOM-ORG-1KG",
            barcode="890123450001",
            name="Organic Farm-Fresh Hybrid Tomatoes",
            slug="organic-farm-fresh-hybrid-tomatoes",
            brand="FarmDirect",
            description="Vine-ripened, naturally grown juicy hybrid red tomatoes packed with lycopene and vitamin C.",
            category_id=cat_veggies.id,
            unit="kg",
            base_price=48.0,
            sale_price=42.0,
            tax_rate=0.0,
            is_variable_weight=True,
            weight_increment=0.5,
            weight_tolerance_pct=15.0,
            is_organic=True,
            is_vegetarian=True,
            is_vegan=True,
            status="ACTIVE",
            rating_average=4.8,
            rating_count=24,
        )
        # Onions (Variable weight)
        p_onions = Product(
            sku="PROD-ONN-NAS-1KG",
            barcode="890123450002",
            name="Fresh Nashik Red Onions",
            slug="fresh-nashik-red-onions",
            brand="FarmDirect",
            description="Crisp and pungent high-grade Nashik red onions.",
            category_id=cat_veggies.id,
            unit="kg",
            base_price=35.0,
            sale_price=28.0,
            tax_rate=0.0,
            is_variable_weight=True,
            weight_increment=1.0,
            weight_tolerance_pct=10.0,
            is_organic=False,
            is_vegetarian=True,
            is_vegan=True,
            status="ACTIVE",
            rating_average=4.6,
            rating_count=18,
        )
        # Apples (Fixed pack)
        p_apples = Product(
            sku="PROD-APL-ROYAL-4PC",
            barcode="890123450003",
            name="Royal Gala Crisp Red Apples 4-Pack",
            slug="royal-gala-crisp-red-apples-4-pack",
            brand="Himalayan Orchards",
            description="Hand-picked sweet and juicy premium crisp Royal Gala apples.",
            category_id=cat_fruits.id,
            unit="pack",
            base_price=190.0,
            sale_price=165.0,
            tax_rate=0.0,
            is_variable_weight=False,
            is_organic=True,
            is_vegetarian=True,
            is_vegan=True,
            status="ACTIVE",
            rating_average=4.9,
            rating_count=32,
        )
        # Amul Butter (Fixed pack)
        p_butter = Product(
            sku="PROD-BTR-AMUL-500G",
            barcode="890123450004",
            name="Amul Pasteurised Butter 500g",
            slug="amul-pasteurised-butter-500g",
            brand="Amul",
            description="The taste of India - delicious creamy salted table butter.",
            category_id=cat_milk.id,
            unit="pack",
            base_price=285.0,
            sale_price=275.0,
            tax_rate=5.0,
            is_variable_weight=False,
            is_vegetarian=True,
            status="ACTIVE",
            rating_average=4.9,
            rating_count=150,
        )
        # Mother Dairy Butter (Substitute for Amul)
        p_md_butter = Product(
            sku="PROD-BTR-MD-500G",
            barcode="890123450005",
            name="Mother Dairy Pure Table Butter 500g",
            slug="mother-dairy-pure-table-butter-500g",
            brand="Mother Dairy",
            description="Rich and creamy salted table butter made from pure milk cream.",
            category_id=cat_milk.id,
            unit="pack",
            base_price=280.0,
            sale_price=270.0,
            tax_rate=5.0,
            is_variable_weight=False,
            is_vegetarian=True,
            status="ACTIVE",
            rating_average=4.7,
            rating_count=45,
        )
        # Daawat Basmati Rice 5kg
        p_rice = Product(
            sku="PROD-RCE-DAAWAT-5KG",
            barcode="890123450006",
            name="Daawat Rozana Gold Basmati Rice 5kg",
            slug="daawat-rozana-gold-basmati-rice-5kg",
            brand="Daawat",
            description="Aromatic, aged long-grain basmati rice for daily family meals.",
            category_id=cat_rice.id,
            unit="bag",
            base_price=580.0,
            sale_price=520.0,
            tax_rate=0.0,
            is_variable_weight=False,
            is_vegetarian=True,
            is_gluten_free=True,
            status="ACTIVE",
            rating_average=4.8,
            rating_count=88,
        )
        # Puvi Cold Pressed Oil 1L
        p_oil = Product(
            sku="PROD-OIL-PUVI-1L",
            barcode="890123450007",
            name="Puvi Cold Pressed Groundnut Oil 1L",
            slug="puvi-cold-pressed-groundnut-oil-1l",
            brand="Puvi",
            description="Traditional wooden cold-pressed groundnut oil, 100% pure & unrefined.",
            category_id=cat_oils.id,
            unit="bottle",
            base_price=260.0,
            sale_price=235.0,
            tax_rate=5.0,
            is_variable_weight=False,
            is_organic=True,
            is_vegetarian=True,
            is_vegan=True,
            status="ACTIVE",
            rating_average=4.9,
            rating_count=64,
        )

        all_products = [p_tomatoes, p_onions, p_apples, p_butter, p_md_butter, p_rice, p_oil]
        session.add_all(all_products)
        await session.flush()

        # Product Images
        images = [
            ProductImage(product_id=p_tomatoes.id, image_url="https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500", is_primary=True),
            ProductImage(product_id=p_onions.id, image_url="https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500", is_primary=True),
            ProductImage(product_id=p_apples.id, image_url="https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500", is_primary=True),
            ProductImage(product_id=p_butter.id, image_url="https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500", is_primary=True),
            ProductImage(product_id=p_md_butter.id, image_url="https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500", is_primary=True),
            ProductImage(product_id=p_rice.id, image_url="https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500", is_primary=True),
            ProductImage(product_id=p_oil.id, image_url="https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500", is_primary=True),
        ]
        session.add_all(images)

        # Smart Substitution Rule: Amul Butter <-> Mother Dairy Butter
        sub_rule = ProductSubstitutionRule(
            original_product_id=p_butter.id,
            substitute_product_id=p_md_butter.id,
            priority_score=0.95,
            is_approved=True,
        )
        session.add(sub_rule)

        print("[*] Seeding Multi-Vendor Marketplace, Stores, and Warehouses...")
        # 4. Vendors & Stores
        vendor = Vendor(
            owner_id=vendor_owner.id,
            business_name="Green Leaf Organics Pvt Ltd",
            slug="green-leaf-organics",
            email="support@greenleaf.com",
            phone="+919000000002",
            tax_id="36AABCB1234D1Z5",
            kyc_status="APPROVED",
            is_active=True,
        )
        session.add(vendor)
        await session.flush()

        v_store = VendorStore(
            vendor_id=vendor.id,
            store_name="Green Leaf Hitec City Hub",
            address_street="Building 5, Mindspace IT Park, Madhapur",
            city="Hyderabad",
            state="Telangana",
            postal_code="500081",
            latitude=17.4435,
            longitude=78.3772,
            delivery_radius_km=15.0,
            is_accepting_orders=True,
        )
        session.add(v_store)

        # Central Warehouse
        warehouse = Warehouse(
            code="WH-HYD-CENTRAL-01",
            name="Hyderabad Central Fulfillment Center",
            type="CENTRAL_WAREHOUSE",
            address="Survey 45, Gachibowli Outer Ring Road",
            city="Hyderabad",
            latitude=17.4400,
            longitude=78.3489,
            is_active=True,
        )
        session.add(warehouse)
        await session.flush()

        print("[*] Seeding FEFO Inventory Lots with Dual Expiration Dates...")
        # 5. Inventory Batches
        now = datetime.now(timezone.utc)
        batches = [
            InventoryBatch(
                batch_number="LOT-TOM-2026-001",
                product_id=p_tomatoes.id,
                warehouse_id=warehouse.id,
                vendor_id=vendor.id,
                manufacturing_date=now - timedelta(days=1),
                expiry_date=now + timedelta(days=6),
                initial_qty=250.0,
                available_qty=250.0,
                reserved_qty=0.0,
                procurement_cost=30.0,
                status="ACTIVE",
            ),
            InventoryBatch(
                batch_number="LOT-BTR-2026-001",
                product_id=p_butter.id,
                warehouse_id=warehouse.id,
                vendor_id=vendor.id,
                manufacturing_date=now - timedelta(days=10),
                expiry_date=now + timedelta(days=180),
                initial_qty=500.0,
                available_qty=500.0,
                reserved_qty=0.0,
                procurement_cost=220.0,
                status="ACTIVE",
            ),
            InventoryBatch(
                batch_number="LOT-RCE-2026-001",
                product_id=p_rice.id,
                warehouse_id=warehouse.id,
                vendor_id=vendor.id,
                manufacturing_date=now - timedelta(days=20),
                expiry_date=now + timedelta(days=730),
                initial_qty=300.0,
                available_qty=300.0,
                reserved_qty=0.0,
                procurement_cost=410.0,
                status="ACTIVE",
            ),
            InventoryBatch(
                batch_number="LOT-OIL-2026-001",
                product_id=p_oil.id,
                warehouse_id=warehouse.id,
                vendor_id=vendor.id,
                manufacturing_date=now - timedelta(days=5),
                expiry_date=now + timedelta(days=365),
                initial_qty=400.0,
                available_qty=400.0,
                reserved_qty=0.0,
                procurement_cost=185.0,
                status="ACTIVE",
            ),
        ]
        session.add_all(batches)

        print("[*] Seeding Promotional Discount Coupons...")
        # 6. Coupons
        coupons = [
            Coupon(
                code="FRESHSTART",
                description="Flat ₹100 Off on your first order above ₹500",
                discount_type="FIXED_AMOUNT",
                discount_value=100.0,
                min_order_value=500.0,
                is_first_order_only=True,
                usage_limit_per_user=1,
                starts_at=now,
                expires_at=now + timedelta(days=60),
                is_active=True,
            ),
            Coupon(
                code="ORGANIC20",
                description="20% Discount up to ₹150 on fresh organic groceries",
                discount_type="PERCENTAGE",
                discount_value=20.0,
                min_order_value=400.0,
                max_discount_cap=150.0,
                is_first_order_only=False,
                usage_limit_per_user=5,
                starts_at=now,
                expires_at=now + timedelta(days=90),
                is_active=True,
            ),
            Coupon(
                code="WEEKEND50",
                description="Flat ₹50 Off on weekend orders above ₹300",
                discount_type="FIXED_AMOUNT",
                discount_value=50.0,
                min_order_value=300.0,
                is_first_order_only=False,
                usage_limit_per_user=10,
                starts_at=now,
                expires_at=now + timedelta(days=30),
                is_active=True,
            ),
        ]
        session.add_all(coupons)

        print("[*] Seeding Delivery Zones and Scheduled Slots...")
        # 7. Delivery Zones & Slots
        zone_hyd = DeliveryZone(
            name="Hyderabad Cyberabad Zone",
            code="HYD-CYBER-01",
            city="Hyderabad",
            state="Telangana",
            center_latitude=17.4435,
            center_longitude=78.3772,
            radius_km=18.0,
            base_fee=35.0,
            is_active=True,
        )
        session.add(zone_hyd)
        await session.flush()

        today_d = date.today()
        for d_offset in range(3):
            slot_d = today_d + timedelta(days=d_offset)
            slot_configs = [
                ("07:00", "09:00", "STANDARD_2HOUR", 30),
                ("09:00", "11:00", "STANDARD_2HOUR", 40),
                ("11:00", "13:00", "STANDARD_2HOUR", 35),
                ("14:00", "16:00", "STANDARD_2HOUR", 30),
                ("16:00", "18:00", "STANDARD_2HOUR", 45),
                ("18:00", "20:00", "STANDARD_2HOUR", 50),
                ("20:00", "22:00", "STANDARD_2HOUR", 35),
            ]
            for start_t, end_t, stype, cap in slot_configs:
                session.add(
                    DeliverySlot(
                        zone_id=zone_hyd.id,
                        slot_date=slot_d,
                        start_time=start_t,
                        end_time=end_t,
                        slot_type=stype,
                        max_capacity=cap,
                        current_bookings=0,
                        is_active=True,
                    )
                )

        await session.commit()
        print("[SUCCESS] Master grocery dataset successfully seeded with complete taxonomy, multi-vendor stores, lots, coupons, and delivery zones!")


if __name__ == "__main__":
    asyncio.run(seed_master_dataset())
