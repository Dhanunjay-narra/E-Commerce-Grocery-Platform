"""Configuration settings for the FreshCart Grocery Application."""
import json
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "FreshCart Grocery Platform"
    API_V1_STR: str = "/api/v1"
    PROJECT_VERSION: str = "1.0.0"

    # Security & Tokens
    SECRET_KEY: str = "freshcart-super-secret-production-grade-key-change-in-prod-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_SECONDS: int = 300  # 5 minutes
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./freshcart.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis Cache & Locks
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    STOCK_RESERVATION_TTL_SECONDS: int = 600  # 10 minutes cart hold

    # Celery & RabbitMQ
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        elif isinstance(v, list):
            return v
        return []

    # Grocery Logistics & Deliveries
    DEFAULT_DELIVERY_RADIUS_KM: float = 15.0
    EXPRESS_DELIVERY_WINDOW_MINUTES: int = 30
    SLOT_CAPACITY_PER_WINDOW: int = 25
    BASE_DELIVERY_FEE: float = 40.0
    FREE_DELIVERY_THRESHOLD: float = 500.0

    # Variable Weight Pricing
    DEFAULT_WEIGHT_TOLERANCE_PERCENTAGE: float = 15.0  # Allow +/- 15% picked weight delta

    # Payment Gateway Mode
    PAYMENT_GATEWAY_MODE: str = "mock"  # "mock" | "stripe" | "razorpay"
    STRIPE_API_KEY: Optional[str] = "sk_test_mock_stripe_key"
    RAZORPAY_KEY_ID: Optional[str] = "rzp_test_mock_key"
    RAZORPAY_KEY_SECRET: Optional[str] = "mock_razorpay_secret"

    # Notification & SMTP
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = "notifications@freshcart.com"
    SMTP_PASSWORD: Optional[str] = "mock_smtp_password"
    EMAILS_FROM_EMAIL: str = "support@freshcart.com"
    EMAILS_FROM_NAME: str = "FreshCart Grocery"

    # OpenSearch
    SEARCH_ENGINE_URL: str = "http://localhost:9200"
    SEARCH_INDEX_PREFIX: str = "freshcart"


settings = Settings()
