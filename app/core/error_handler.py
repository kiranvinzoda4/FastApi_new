import logging
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
logger = logging.getLogger("app.errors")
class ErrorHandler:
    """Centralized error handling for the entire application"""
    @staticmethod
    def handle_exception(e: Exception, context: str = "") -> HTTPException:
        """Convert any exception to appropriate HTTPException"""
        if isinstance(e, HTTPException):
            return e
        if isinstance(e, ValidationError):
            logger.warning(f"Validation error{f' in {context}' if context else ''}: {e}")
            return HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid input data")
        if isinstance(e, ValueError):
            logger.warning(f"Value error{f' in {context}' if context else ''}: {e}")
            return HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
        if isinstance(e, IntegrityError):
            logger.error(f"Database integrity error{f' in {context}' if context else ''}: {e}")
            return HTTPException(status.HTTP_409_CONFLICT, "Data conflict occurred")
        if isinstance(e, SQLAlchemyError):
            logger.error(f"Database error{f' in {context}' if context else ''}: {e}")
            return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error")
        logger.error(f"Unexpected error{f' in {context}' if context else ''}: {e}", exc_info=True)
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
def handle_errors(func: Callable) -> Callable:
    """Decorator for centralized error handling"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            raise ErrorHandler.handle_exception(e, func.__name__)
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ErrorHandler.handle_exception(e, func.__name__)
    return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for FastAPI"""
    http_exc = ErrorHandler.handle_exception(exc, f"{request.method} {request.url.path}")
    return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": http_exc.detail}
    )
