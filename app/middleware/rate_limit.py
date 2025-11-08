import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Method-based rate limits
RATE_LIMITS = {
    "GET": "200/minute",      # Read operations - higher limit
    "POST": "50/minute",     # Create operations - medium limit  
    "PUT": "50/minute",      # Update operations - medium limit
    "PATCH": "50/minute",    # Partial update - medium limit
    "DELETE": "20/minute",   # Delete operations - lower limit
}

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute", "1000/hour"]
)

class SmartRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get method-specific limit
        method_limit = RATE_LIMITS.get(request.method, "100/minute")
        
        # Apply rate limit based on method
        try:
            # Check if limit exceeded
            limiter.check_request_limit(request, method_limit)
            response = await call_next(request)
            return response
        except RateLimitExceeded as e:
            return await rate_limit_handler(request, e)

async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom rate limit exceeded handler"""
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)} "
        f"on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            # amazonq-ignore-next-line
            "retry_after": exc.retry_after
        },
        headers={"Retry-After": str(exc.retry_after)}
    )

def setup_rate_limiting(app):
    """Setup smart rate limiting for the application"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_middleware(SmartRateLimitMiddleware)