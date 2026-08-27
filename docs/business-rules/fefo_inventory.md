# FEFO (First-Expiry, First-Out) Inventory Fulfillment Rules

Grocery supply chains deal with perishables (milk, yogurt, fresh berries, bakery, meat, vegetables) where minimizing food waste requires strictly adhering to **FEFO** instead of generic FIFO.

## 1. Batch & Lot Tracking Model
Every batch receipt in the warehouse/store records:
- `batch_number`: Lot identification code
- `product_id`: Master product reference
- `vendor_id`: Supplier / Store reference
- `manufacturing_date`: Timestamp of production
- `expiry_date`: Timestamp of shelf life termination
- `initial_quantity`: Original units received
- `available_quantity`: Current unreserved units
- `reserved_quantity`: Units locked in active carts
- `damaged_quantity`: Spoilage/damaged units removed from sale

## 2. Dynamic Allocation Algorithm
When an order is created:
1. System queries all non-expired batches for `(product_id, vendor_id)` where `available_quantity > 0` and `expiry_date > (now + minimum_shelf_life_buffer)`.
2. Batches are sorted ascending by `expiry_date`:
   $$\text{Sort By: } \min(\text{expiry\_date})$$
3. Stock is reserved sequentially across earliest-expiring batches until requested quantity is fulfilled.
4. If total available quantity across all non-expired batches is less than requested quantity, an `InsufficientInventoryError` is thrown with exact available count.

## 3. Expiry Warning Thresholds
- **Critical (Red)**: Expiry $< 24$ hours $\rightarrow$ Auto-discount banner or mark as clearance.
- **Warning (Yellow)**: Expiry $< 72$ hours $\rightarrow$ Fast-track allocation priority.
- **Expired**: Expiry $< 0$ hours $\rightarrow$ Automatic status change to `EXPIRED`, removed from customer catalog.
