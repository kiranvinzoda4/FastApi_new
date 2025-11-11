import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
# Security scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length: int = 6) -> str:
    """Generate a secure OTP"""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.ACCESS_JWT_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.REFRESH_JWT_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode access token"""
    return jwt.decode(token, settings.ACCESS_JWT_KEY, algorithms=[ALGORITHM])


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify and decode refresh token"""
    return jwt.decode(token, settings.REFRESH_JWT_KEY, algorithms=[ALGORITHM])


async def get_current_user(credentials=Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        payload = verify_access_token(credentials.credentials)
        if not payload.get("sub"):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
        return payload
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
