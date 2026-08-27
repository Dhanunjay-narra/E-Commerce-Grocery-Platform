"""Main FastAPI application entry point with all 18 domain routers registered and lifecycle hooks."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.redis import cache
from app.core.exceptions import register_exception_handlers
from app.core.middleware import RequestContextMiddleware, RateLimitMiddleware

# All 18 Domain Routers
from app.modules.authentication.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.categories.router import router as categories_router
from app.modules.products.router import router as products_router
from app.modules.search.router import router as search_router
from app.modules.vendors.router import router as vendors_router
from app.modules.inventory.router import router as inventory_router
from app.modules.cart.router import router as cart_router
from app.modules.wishlist.router import router as wishlist_router
from app.modules.coupons.router import router as coupons_router
from app.modules.shipping.router import router as shipping_router
from app.modules.payments.router import router as payments_router
from app.modules.orders.router import router as orders_router
from app.modules.substitutions.router import router as substitutions_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.reviews.router import router as reviews_router
from app.modules.notifications.router import router as notifications_router
from app.modules.admin.router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle manager."""
    # Startup
    await init_db()
    await cache.initialize()
    yield
    # Shutdown
    await cache.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.PROJECT_VERSION,
    description="Production-Ready Modular E-Commerce Grocery & Logistics Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Exception handlers
register_exception_handlers(app)

# Custom middlewares
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests_per_minute=200)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(users_router, prefix=api_v1_prefix)
app.include_router(categories_router, prefix=api_v1_prefix)
app.include_router(products_router, prefix=api_v1_prefix)
app.include_router(search_router, prefix=api_v1_prefix)
app.include_router(vendors_router, prefix=api_v1_prefix)
app.include_router(inventory_router, prefix=api_v1_prefix)
app.include_router(cart_router, prefix=api_v1_prefix)
app.include_router(wishlist_router, prefix=api_v1_prefix)
app.include_router(coupons_router, prefix=api_v1_prefix)
app.include_router(shipping_router, prefix=api_v1_prefix)
app.include_router(payments_router, prefix=api_v1_prefix)
app.include_router(orders_router, prefix=api_v1_prefix)
app.include_router(substitutions_router, prefix=api_v1_prefix)
app.include_router(recommendations_router, prefix=api_v1_prefix)
app.include_router(reviews_router, prefix=api_v1_prefix)
app.include_router(notifications_router, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check probe endpoint for Kubernetes / Docker orchestrators."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API. Visit /docs for OpenAPI documentation.",
        "version": settings.PROJECT_VERSION,
    }
