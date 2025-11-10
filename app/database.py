import logging
from typing import Optional
from sqlalchemy import create_engine, text, event, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.config import settings
logger = logging.getLogger(__name__)
class DatabaseManager:
    def __init__(self) -> None:
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_database()
    def _initialize_database(self) -> None:
        """Initialize database connection with proper error handling"""
        try:
            # Validate configuration
            if not all([settings.DB_USER, settings.DB_PASSWORD, settings.DB_HOST, settings.DB_NAME]):
                raise ValueError("Missing required database configuration")
            # Calculate pool size
            pool_size: int = max(settings.DB_POOL_SIZE // settings.WEB_CONCURRENCY, 5)
            # Create database if it doesn't exist
            self._create_database_if_not_exists()
            # Create main engine
            database_url: str = (
                f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            )
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=0,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=settings.DEBUG,  # Log SQL queries in debug mode
            )
            # Add connection event listeners
            self._setup_connection_events()
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            # Test connection
            self._test_connection()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")
    def _create_database_if_not_exists(self) -> None:
        """Create database if it doesn't exist"""
        try:
            temp_url: str = (
                f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}/"
            )
            temp_engine: Engine = create_engine(temp_url)
            with temp_engine.connect() as connection:
                # Comprehensive database name validation
                db_name = self._validate_database_name(settings.DB_NAME)
                # Use safe identifier quoting
                safe_query = text("CREATE DATABASE IF NOT EXISTS `" + db_name + "`")
                connection.execute(safe_query)
                connection.commit()
            temp_engine.dispose()
            logger.info(f"Database '{settings.DB_NAME}' ensured to exist")
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    def _validate_database_name(self, db_name: str) -> str:
        """Validate database name with comprehensive security checks"""
        if not db_name or not isinstance(db_name, str):
            raise ValueError("Database name must be a non-empty string")
        # Remove any potential SQL injection characters
        cleaned_name = db_name.strip()
        # Whitelist approach: only allow specific patterns
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{0,63}$', cleaned_name):
            raise ValueError("Database name must start with letter, contain only alphanumeric and underscore, max 64 chars")
        # Additional security: check against common SQL keywords
        sql_keywords = {'SELECT', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 'UNION'}
        if cleaned_name.upper() in sql_keywords:
            raise ValueError("Database name cannot be a SQL keyword")
        return cleaned_name
    def _setup_connection_events(self) -> None:
        """Setup connection event listeners for monitoring"""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            # This is for MySQL, but we can add connection-specific settings here
            pass
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            logger.debug("Connection checked in to pool")
    def _test_connection(self) -> None:
        """Test database connection"""
        try:
            if not self.engine:
                raise RuntimeError("Engine not initialized")
            with self.engine.connect() as connection:
                # Use parameterized query for safety
                result = connection.execute(text("SELECT :test_value"), {"test_value": 1})
                row = result.fetchone()
                if not row or row[0] != 1:
                    raise RuntimeError("Connection test failed")
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    def get_session(self) -> Session:
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    def close(self) -> None:
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")
# Initialize database manager
db_manager = DatabaseManager()
# Export for backward compatibility
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
Base = declarative_base()
