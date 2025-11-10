from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.dependencies import get_db
from app.config import settings
from app.core.error_handler import handle_errors
from pydantic import BaseModel
router = APIRouter(prefix="/health", tags=["Health Check"])
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str
    environment: str
class DetailedHealthResponse(HealthResponse):
    uptime: str
    database_connection: bool
    email_service: bool
@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database="connected",
        environment="production" if not settings.DEBUG else "development"
    )
@router.get("/detailed", response_model=DetailedHealthResponse)
@handle_errors
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with service status"""
    # Check database connection
    db_healthy = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_healthy = False
    # Check email service configuration
    email_healthy = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
    # Overall status
    overall_status = "healthy" if db_healthy and email_healthy else "unhealthy"
    if not db_healthy or not email_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="One or more services are unhealthy"
        )
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database="connected" if db_healthy else "disconnected",
        environment="production" if not settings.DEBUG else "development",
        uptime="N/A",  # Could implement actual uptime tracking
        database_connection=db_healthy,
        email_service=email_healthy
    )
@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}
