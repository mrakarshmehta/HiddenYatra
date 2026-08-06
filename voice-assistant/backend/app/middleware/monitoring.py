import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("voice_assistant_monitoring")

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Production monitoring middleware measuring request latency and status."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        logger.info(f"Path: {request.url.path} | Status: {response.status_code} | Latency: {process_time:.2f}ms")
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        return response
