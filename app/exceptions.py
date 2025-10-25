import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class CustomException(Exception):
    """Base custom exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseException(CustomException):
    """Database related exceptions"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class ValidationException(CustomException):
    """Validation related exceptions"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class AuthenticationException(CustomException):
    """Authentication related exceptions"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationException(CustomException):
    """Authorization related exceptions"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class NotFoundException(CustomException):
    """Resource not found exceptions"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

async def custom_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions"""
    logger.error(f"Custom exception: {exc.message} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": exc.__class__.__name__}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions with detailed error messages"""
    errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "unknown"
        message = error.get("msg", "Invalid input")
        errors.append({"field": field, "message": message})
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception {exc.status_code}: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database exceptions"""
    logger.error(f"Database error on {request.url.path}: {str(exc)}")
    
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Data integrity constraint violation"}
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )