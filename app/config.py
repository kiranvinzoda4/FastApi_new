import json
import logging
from dotenv import load_dotenv
from pydantic import validator
from pydantic_settings import BaseSettings
# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)
class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_POOL_SIZE: int = 100
    WEB_CONCURRENCY: int = 2
    # JWT Keys - Required for security
    JWT_KEY: str
    ACCESS_JWT_KEY: str  
    REFRESH_JWT_KEY: str
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    # Admin User (for seeding) - SECURITY: No password in config, use secure reset flow
    ADMIN_EMAIL: str = ""
    # ADMIN_PASSWORD removed - use password reset links instead of hardcoded passwords
    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "*"
    @validator('JWT_KEY', 'ACCESS_JWT_KEY', 'REFRESH_JWT_KEY')
    def validate_jwt_keys(cls, v):
        if not v or v.strip() == "":
            raise ValueError("JWT key cannot be empty - must be configured in environment")
        try:
            parsed_key = json.loads(v)
            if not isinstance(parsed_key, dict) or 'k' not in parsed_key:
                raise ValueError("JWT key must be valid JWK format with 'k' field")
            return parsed_key
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Invalid JWT key format: {e}")
            raise ValueError("JWT key must be valid JSON in JWK format")
    @validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v):
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",")]
    class Config:
        env_file = ".env"
        case_sensitive = True
try:
    settings = Settings()
except ValueError as e:
    logger.error(f"Configuration validation error: {e}")
    raise RuntimeError(f"Invalid configuration: {e}")
except FileNotFoundError as e:
    logger.error(f"Environment file not found: {e}")
    raise RuntimeError(f"Environment configuration missing: {e}")
except Exception as e:
    logger.error(f"Unexpected configuration error: {e}")
    raise RuntimeError(f"Failed to load configuration: {e}")
# Export for backward compatibility
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_NAME = settings.DB_NAME
DB_PORT = settings.DB_PORT
JWT_KEY = settings.JWT_KEY
REFRESH_JWT_KEY = settings.REFRESH_JWT_KEY
ACCESS_JWT_KEY = settings.ACCESS_JWT_KEY
