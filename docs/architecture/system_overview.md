# FreshCart Grocery Platform — System Overview & Architecture

## 1. Executive Summary
FreshCart is an enterprise-grade multi-vendor grocery e-commerce and logistics ecosystem designed with a Modular Monolith architecture in FastAPI and Next.js. It features FEFO (First-Expiry, First-Out) perishable inventory management, dynamic capacity-aware delivery slot routing, variable-weight produce checkout reconciliation, smart household replenishment, and algorithmic substitutions.

---

## 2. Layered Domain Architecture

```
                          ┌──────────────────────────┐
                          │   Client Applications    │
                          │ Next.js Web / Mobile Apps│
                          └────────────┬─────────────┘
                                       │ HTTPS / WSS
                                       ▼
                          ┌──────────────────────────┐
                          │   FastAPI API Gateway    │
                          │ Auth / Rate Limit / CORS │
                          └────────────┬─────────────┘
                                       │
               ┌───────────────────────┼───────────────────────┐
               │                       │                       │
               ▼                       ▼                       ▼
       ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
       │ Customer APIs │       │  Vendor APIs  │       │  Admin APIs   │
       └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
               │                       │                       │
               └───────────────────────┼───────────────────────┘
                                       ▼
                        ┌────────────────────────────┐
                        │  Backend Modular Monolith  │
                        │ 18 Decoupled Domain Modules│
                        └─────────────┬──────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │             │              │             │              │
         ▼             ▼              ▼             ▼              ▼
    PostgreSQL      Redis          Celery      OpenSearch     S3 Storage
  (Async 2.0)    (Cache/Locks)   (Workers)      (Search)      (Media Assets)
```

---

## 3. Core Subsystems

### 3.1 Authentication & Security (RBAC)
- Support for Password, Mobile OTP, Refresh Token Rotation, Session Invalidation.
- 8 Granular Roles:
  - `CUSTOMER`
  - `VENDOR_OWNER`
  - `VENDOR_STAFF`
  - `DELIVERY_AGENT`
  - `SUPPORT_AGENT`
  - `ANALYST`
  - `ADMIN`
  - `SUPER_ADMIN`

### 3.2 FEFO Inventory Engine
- Batches tracking manufacturing date, expiry date, procurement cost, and vendor origin.
- Automatic allocation prioritizes batches closest to expiration to minimize waste.
- Stock reservation with TTL locks upon checkout initiation.

### 3.3 Variable-Weight Produce Fulfillment
- Supports pricing per kg/pack with estimated pre-authorization.
- Picker weighs actual item at fulfillment station (e.g. 1.08 kg vs 1.00 kg).
- Final charge reconciled upon packing.

### 3.4 Delivery Slot Engine
- Dynamic slots (Express 30-min, 2-hour scheduled windows).
- Real-time zone geofencing, driver capacity checks, and vendor picking readiness.
