import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.routers.admin import api as admin
from app.config import settings
from app.logging_config import setup_logging
from app.database import db_manager
from app.project_info import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION
from app.middleware.error_logging import ErrorLoggingMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {PROJECT_NAME}")
    yield
    # Shutdown
    logger.info(f"Shutting down {PROJECT_NAME}")
    db_manager.close()

app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan
)

# Security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)

# Error logging middleware
app.add_middleware(ErrorLoggingMiddleware)

# Rate limiting disabled

# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - {process_time:.4f}s"
    )
    
    return response


# Include routers
from app.routers import health
app.include_router(health.router)
app.include_router(admin.router)

# Exception handlers
from app.exceptions import (
    CustomException, custom_exception_handler,
    validation_exception_handler, http_exception_handler,
    database_exception_handler, general_exception_handler
)
from sqlalchemy.exc import SQLAlchemyError

app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Static file mounts
try:
    if os.path.exists(os.path.join("app", "uploads", "images", "vegetables")):
        app.mount(
            "/app/uploads/images/vegetables",
            StaticFiles(directory=os.path.join("app", "uploads", "images", "vegetables")),
            name="vegetable_images"
        )
    
    if os.path.exists(os.path.join("app", "static", "info")):
        app.mount(
            "/static/info",
            StaticFiles(directory=os.path.join("app", "static", "info")),
            name="info_static"
        )
except Exception as e:
    logger.warning(f"Failed to mount static files: {e}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }
