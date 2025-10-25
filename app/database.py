import logging
from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection with proper error handling"""
        try:
            # Calculate pool size
            pool_size = max(settings.DB_POOL_SIZE // settings.WEB_CONCURRENCY, 5)
            
            # Create database if it doesn't exist
            self._create_database_if_not_exists()
            
            # Create main engine
            database_url = (
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
    
    def _create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            temp_url = (
                f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}/"
            )
            temp_engine = create_engine(temp_url)
            
            with temp_engine.connect() as connection:
                connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}`"))
                connection.commit()
            
            temp_engine.dispose()
            logger.info(f"Database '{settings.DB_NAME}' ensured to exist")
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def _setup_connection_events(self):
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
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def close(self):
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
