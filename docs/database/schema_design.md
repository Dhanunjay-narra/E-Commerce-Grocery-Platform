# FreshCart Database Schema & Relational Design

The database schema is organized across 18 modular domains with foreign key constraints, indexes, and soft-deletion tracking.

## Core ER Model

```mermaid
erDiagram
    USERS ||--o{ USER_ADDRESSES : has
    USERS ||--o| USER_PROFILES : has
    USERS ||--o| DIETARY_PREFERENCES : has
    USERS ||--o{ HOUSEHOLD_MEMBERS : belongs_to
    HOUSEHOLDS ||--o{ HOUSEHOLD_MEMBERS : includes
    HOUSEHOLDS ||--o{ HOUSEHOLD_SHOPPING_ITEMS : contains

    CATEGORIES ||--o{ CATEGORIES : parent_child
    CATEGORIES ||--o{ PRODUCTS : categorizes
    VENDORS ||--o{ PRODUCTS : supplies
    VENDORS ||--o{ INVENTORY_BATCHES : stocks
    PRODUCTS ||--o{ INVENTORY_BATCHES : has_lots

    CARTS ||--o{ CART_ITEMS : holds
    PRODUCTS ||--o{ CART_ITEMS : referenced_in

    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--|| PAYMENTS : settled_by
    ORDERS ||--|| SHIPMENTS : fulfilled_by
    SHIPMENTS ||--|| DELIVERY_TRACKING : tracks

    PRODUCTS ||--o{ REVIEWS : rated_in
    USERS ||--o{ REVIEWS : writes
    COUPONS ||--o{ COUPON_REDEMPTIONS : redeemed_by
```

## Schema Entities Summary

1. **Identity & Auth**: `users`, `user_profiles`, `user_addresses`, `dietary_preferences`, `user_sessions`, `refresh_tokens`, `otp_records`, `login_history`.
2. **Households**: `households`, `household_members`, `household_shopping_items`.
3. **Catalog**: `categories`, `products`, `product_variants`, `product_images`.
4. **Inventory**: `vendors`, `inventory_batches`, `inventory_transactions`, `stock_reservations`.
5. **Commerce**: `carts`, `cart_items`, `wishlists`, `wishlist_items`, `coupons`, `coupon_redemptions`.
6. **Orders & Logistics**: `orders`, `order_items`, `order_status_history`, `order_fulfillments`, `payments`, `payment_refunds`, `delivery_zones`, `delivery_slots`, `shipments`.
7. **Intelligence & BI**: `smart_grocery_plans`, `replenishment_schedules`, `substitution_logs`, `reviews`, `notification_logs`, `admin_audit_logs`.
