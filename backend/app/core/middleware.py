"""Application middlewares: request timing, correlation IDs, rate limiting."""
import time
import uuid
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger
from app.core.redis import cache


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Injects X-Request-ID and logs latency and status code."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        response: Response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)

        # Skip spammy healthcheck logs
        if request.url.path not in ["/health", "/docs", "/openapi.json"]:
            logger.info(
                f"{request.method} {request.url.path} {response.status_code} - {process_time_ms}ms"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window or counter rate limiting per client IP."""

    def __init__(self, app, max_requests_per_minute: int = 120):
        super().__init__(app)
        self.max_requests = max_requests_per_minute

    async def dispatch(self, request: Request, call_next):
        # Exclude static/health docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        cache_key = f"ratelimit:{client_ip}:{int(time.time() // 60)}"

        try:
            current_count = await cache.incr(cache_key)
            if current_count == 1:
                await cache.expire(cache_key, 60)

            if current_count > self.max_requests:
                return Response(
                    content='{"success": false, "error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests. Please slow down."}}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                )
        except Exception:
            pass  # Fallthrough on cache errors to not block legitimate traffic

        return await call_next(request)
