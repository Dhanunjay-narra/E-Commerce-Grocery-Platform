# E-Commerce Grocery Platform (FreshCart) 🛒🥦🥖

A modern, production-grade, API-first **Multi-Vendor Grocery E-Commerce & Logistics Platform** designed with a clean Modular Monolith architecture, intelligent grocery planning, FEFO (First-Expiry, First-Out) inventory fulfillment, variable-weight checkout reconciliation, capacity-aware delivery slot routing, and household shared cart management.

[![CI/CD Pipeline](https://github.com/Dhanunjay-narra/E-Commerce-Grocery-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Dhanunjay-narra/E-Commerce-Grocery-Platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.0+-black.svg)](https://nextjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38bdf8.svg)](https://tailwindcss.com/)

---

## 🌟 Key Differentiating Features

1. **Smart Grocery Planner & Meal Pantry**:
   - Organize weekly household replenishment across produce, dairy, bakery, meat, and staples.
   - Learns household purchase frequencies (e.g. Milk every 3 days, Bread weekly, Cooking Oil monthly) to deliver predictive replenishment alerts.

2. **Variable-Weight Grocery Checkout**:
   - Seamlessly handles produce and butcher items priced per kg (e.g. Tomatoes, Apples, Cheese).
   - Authorizes an estimated charge at checkout, tracks actual picker weight upon packing (e.g. 1.08 kg vs 1.00 kg), and automatically reconciles the final invoice.

3. **FEFO Inventory Fulfillment Engine**:
   - First-Expiry, First-Out lot and batch allocation prevents spoilage and prioritizes older batches for fulfillment.
   - Real-time stock reservation with expiring TTL locks during customer checkout.

4. **Multi-Vendor Grocery Marketplace**:
   - Partitioned shopping cart allowing items from multiple local stores and dark stores.
   - Split fulfillment workflows, vendor KYC onboarding, automated commission settlement, and isolated vendor dashboards.

5. **Intelligent Capacity-Aware Delivery Slots**:
   - Dynamic delivery slot generator (e.g., Express 30-min, 08:00-10:00, 10:00-12:00) factoring in delivery zone geofencing, driver capacity, and vendor packing readiness.

6. **Smart Substitutions System**:
   - Algorithmic fallback suggestion engine for out-of-stock items based on category, brand preference, price delta, and pack size.
   - Configurable per user: *Always substitute*, *Notify & ask me first*, or *Never substitute*.

7. **Household Collaboration**:
   - Shared household shopping lists with real-time sync across family members.

8. **Enterprise RBAC & Security Audit Logs**:
   - 8 distinct roles (`CUSTOMER`, `VENDOR_OWNER`, `VENDOR_STAFF`, `DELIVERY_AGENT`, `SUPPORT_AGENT`, `ANALYST`, `ADMIN`, `SUPER_ADMIN`).
   - Immutable audit logs capturing every price change, stock override, and admin moderation action with before/after diffs.

---

## 🏛️ System Architecture

```
                         ┌──────────────────────────┐
                         │       Client Layer       │
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

## 📦 Domain Modules Overview

| # | Module | Responsibility & Scope |
|---|---|---|
| 1 | **Users** | Customer profiles, address geocoding, dietary preferences, household shared lists. |
| 2 | **Authentication** | Email/Password, Mobile OTP, JWT access/refresh rotation, MFA, session revocation, RBAC. |
| 3 | **Products** | Master catalog, SKU, barcode, nutritional/allergen info, variable weight pricing rules. |
| 4 | **Categories** | 3-tier Department -> Category -> Subcategory hierarchy, SEO metadata, banners. |
| 5 | **Search** | Full-text search with typo tolerance, autocomplete, faceted filtering, dietary filters. |
| 6 | **Cart** | Multi-vendor cart partitioning, variable weight estimation, real-time stock checks. |
| 7 | **Wishlist** | Multiple named wishlists, household sharing, price-drop & back-in-stock alerts. |
| 8 | **Orders** | 11-stage order lifecycle state machine, split vendor fulfillment, variable weight reconciliation. |
| 9 | **Payments** | Idempotent transaction processing, mock payment gateway (UPI/Card/COD), refund tracking. |
| 10 | **Shipping** | Delivery zones, capacity-aware delivery slot engine, delivery agent assignment, OTP POD. |
| 11 | **Inventory** | FEFO batch tracking, multi-warehouse stock, TTL reservations, waste & damage logs. |
| 12 | **Substitutions** | Intelligent alternative suggestion engine for unavailable items with user preferences. |
| 13 | **Reviews** | Verified buyer product & vendor reviews, ratings aggregation, moderation queue. |
| 14 | **Coupons** | Discount rules (percent/fixed), min order, max cap, vendor/category rules, stacking checks. |
| 15 | **Vendors** | Marketplace onboarding, KYC, store operating hours, picking station, payout settlements. |
| 16 | **Notifications**| Multi-channel event router (In-App, simulated Email, SMS, Push, WhatsApp). |
| 17 | **Recommendations**| Smart replenishment cadence model, frequently bought together, recipe match. |
| 18 | **Analytics & Admin**| Platform GMV/AOV BI metrics, vendor scorecards, immutable admin audit logging. |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker & Docker Compose (Optional for local containerized stack)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env

# Run database migrations and seed data
python ../scripts/seed_data.py

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:3000`.

### 3. Running with Docker Compose
```bash
docker-compose up --build
```

---

## 🧪 Testing Suite

Run full backend test suite:
```bash
cd backend
pytest -v
```

---

## 📄 License
This project is open-source software licensed under the [MIT License](LICENSE).
