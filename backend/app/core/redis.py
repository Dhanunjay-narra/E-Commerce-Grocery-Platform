"""Async Redis client manager with transparent in-memory fallback for local dev & testing."""
import asyncio
import time
from typing import Any, Dict, Optional, Tuple
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logging import logger


class InMemoryCache:
    """In-memory fallback cache with TTL expiration and atomic operations."""

    def __init__(self):
        self._store: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._locks: Dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        if key not in self._store:
            return True
        val, exp = self._store[key]
        if exp is not None and time.time() > exp:
            del self._store[key]
            return True
        return False

    async def get(self, key: str) -> Optional[str]:
        if self._is_expired(key):
            return None
        return str(self._store[key][0])

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        exp_time = time.time() + ex if ex else None
        self._store[key] = (value, exp_time)
        return True

    async def delete(self, key: str) -> int:
        if key in self._store:
            del self._store[key]
            return 1
        return 0

    async def exists(self, key: str) -> int:
        return 0 if self._is_expired(key) else 1

    async def incr(self, key: str) -> int:
        if self._is_expired(key):
            self._store[key] = (1, None)
            return 1
        val, exp = self._store[key]
        new_val = int(val) + 1
        self._store[key] = (new_val, exp)
        return new_val

    async def expire(self, key: str, seconds: int) -> bool:
        if key in self._store:
            val, _ = self._store[key]
            self._store[key] = (val, time.time() + seconds)
            return True
        return False

    async def acquire_lock(self, lock_key: str, ttl_seconds: int = 10) -> bool:
        now = time.time()
        if lock_key in self._locks:
            if self._locks[lock_key] > now:
                return False
        self._locks[lock_key] = now + ttl_seconds
        return True

    async def release_lock(self, lock_key: str) -> bool:
        if lock_key in self._locks:
            del self._locks[lock_key]
            return True
        return False


class CacheManager:
    """Unified cache interface dispatching to Redis or In-Memory fallback."""

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._fallback = InMemoryCache()
        self._use_fallback = False

    async def initialize(self) -> None:
        try:
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
            )
            await self._redis.ping()
            logger.info("Connected to Redis successfully.")
            self._use_fallback = False
        except Exception as e:
            logger.warning(f"Redis unavailable ({str(e)}). Utilizing high-speed in-memory cache fallback.")
            self._use_fallback = True

    async def get(self, key: str) -> Optional[str]:
        if self._use_fallback or not self._redis:
            return await self._fallback.get(key)
        try:
            return await self._redis.get(key)
        except Exception:
            return await self._fallback.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        if self._use_fallback or not self._redis:
            return await self._fallback.set(key, value, ex=ex)
        try:
            return await self._redis.set(key, value, ex=ex)
        except Exception:
            return await self._fallback.set(key, value, ex=ex)

    async def delete(self, key: str) -> int:
        if self._use_fallback or not self._redis:
            return await self._fallback.delete(key)
        try:
            return await self._redis.delete(key)
        except Exception:
            return await self._fallback.delete(key)

    async def exists(self, key: str) -> int:
        if self._use_fallback or not self._redis:
            return await self._fallback.exists(key)
        try:
            return await self._redis.exists(key)
        except Exception:
            return await self._fallback.exists(key)

    async def incr(self, key: str) -> int:
        if self._use_fallback or not self._redis:
            return await self._fallback.incr(key)
        try:
            return await self._redis.incr(key)
        except Exception:
            return await self._fallback.incr(key)

    async def expire(self, key: str, seconds: int) -> bool:
        if self._use_fallback or not self._redis:
            return await self._fallback.expire(key, seconds)
        try:
            return await self._redis.expire(key, seconds)
        except Exception:
            return await self._fallback.expire(key, seconds)

    async def acquire_lock(self, lock_key: str, ttl_seconds: int = 10) -> bool:
        if self._use_fallback or not self._redis:
            return await self._fallback.acquire_lock(lock_key, ttl_seconds)
        try:
            acquired = await self._redis.set(f"lock:{lock_key}", "1", nx=True, ex=ttl_seconds)
            return bool(acquired)
        except Exception:
            return await self._fallback.acquire_lock(lock_key, ttl_seconds)

    async def release_lock(self, lock_key: str) -> bool:
        if self._use_fallback or not self._redis:
            return await self._fallback.release_lock(lock_key)
        try:
            await self._redis.delete(f"lock:{lock_key}")
            return True
        except Exception:
            return await self._fallback.release_lock(lock_key)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()


cache = CacheManager()
