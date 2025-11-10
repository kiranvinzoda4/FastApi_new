import logging
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.database import SessionLocal
from app.exceptions import DatabaseException
logger = logging.getLogger(__name__)
def get_db() -> Generator[Session, None, None]:
    """Database dependency with proper error handling"""
    db = None
    try:
        db = SessionLocal()
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        if db:
            db.rollback()
        raise DatabaseException("Database connection error")
    except Exception as e:
        logger.error(f"Unexpected error in database dependency: {e}")
        if db:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database service unavailable"
        )
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
