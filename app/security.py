import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.exceptions import AuthenticationException, AuthorizationException

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security scheme
security = HTTPBearer()

class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a secure OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, settings.ACCESS_JWT_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise AuthenticationException("Failed to create access token")
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, settings.REFRESH_JWT_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise AuthenticationException("Failed to create refresh token")
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            key = settings.ACCESS_JWT_KEY if token_type == "access" else settings.REFRESH_JWT_KEY
            payload = jwt.decode(token, key, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise AuthenticationException("Invalid token type")
            
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise AuthenticationException("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise AuthenticationException("Token verification failed")
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

# Dependency for getting current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        payload = SecurityUtils.verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationException("Invalid token payload")
        return payload
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise AuthenticationException("Authentication failed")

# Optional authentication dependency
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user if token is provided, otherwise return None"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = SecurityUtils.verify_token(token, "access")
        return payload
    except Exception:
        return None

# Rate limiting key function
def get_user_id_or_ip(request: Request) -> str:
    """Get user ID from token or fall back to IP address for rate limiting"""
    try:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = SecurityUtils.verify_token(token, "access")
            return f"user:{payload.get('sub', 'unknown')}"
    except Exception:
        pass
    
    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"
    return f"ip:{request.client.host}"