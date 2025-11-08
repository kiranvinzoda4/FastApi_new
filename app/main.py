import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers.admin import api as admin
from app.config import settings
from app.core.logger import setup_logging
from app.core.error_handler import global_exception_handler
from app.database import db_manager
from app.project_info import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION

setup_logging()
logger = logging.getLogger("app.main")

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

# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)


# Include routers
from app.routers import health
app.include_router(health.router)
app.include_router(admin.router)

# Global exception handler
app.add_exception_handler(Exception, global_exception_handler)

# Static file mounts
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }
