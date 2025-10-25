import json
import os
import logging
from typing import List
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
    
    # JWT Keys
    JWT_KEY: str
    ACCESS_JWT_KEY: str
    REFRESH_JWT_KEY: str
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "*"
    
    @validator('JWT_KEY', 'ACCESS_JWT_KEY', 'REFRESH_JWT_KEY')
    def validate_jwt_keys(cls, v):
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Invalid JWT key format: {e}")
            raise ValueError("JWT key must be valid JSON")
    
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
except Exception as e:
    logger.error(f"Configuration error: {e}")
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