from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    Text,
)
from sqlalchemy.orm import relationship, declarative_mixin
import uuid
from app.database import Base


@declarative_mixin
class IDMixin:
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


@declarative_mixin
class SoftDeleteMixin:
    is_deleted = Column(Boolean, nullable=False, default=False)


@declarative_mixin
class NameMixin:
    name = Column(String(100), nullable=False)


class AdminUserModel(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "admin_users"
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(15))
    password = Column(String(255), nullable=False)
    # OTP fields with security
    otp = Column(String(64))  # Store hashed OTP
    otp_expires_at = Column(DateTime)
    otp_attempts = Column(Integer, default=0)
    otp_generated_at = Column(DateTime)
    otp_generation_count = Column(Integer, default=0)
    # Password reset token fields
    reset_token = Column(String(64))  # Secure reset token
    reset_token_expires_at = Column(DateTime)
    reset_token_used = Column(Boolean, default=False)


class APILogModel(Base, IDMixin):
    __tablename__ = "api_logs"
    url = Column(Text, nullable=False)
    method = Column(String(10), nullable=False)
    payload = Column(Text)
    status_code = Column(Integer, nullable=False)
    error_message = Column(Text)
    user_id = Column(String(36))
    user_type = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)


class CountryModel(Base, IDMixin, TimestampMixin, SoftDeleteMixin, NameMixin):
    __tablename__ = "countries"
    code = Column(String(10), nullable=False, unique=True)


class StateModel(Base, IDMixin, TimestampMixin, SoftDeleteMixin, NameMixin):
    __tablename__ = "states"
    code = Column(String(10), nullable=False)
    country_id = Column(String(36), ForeignKey("countries.id"), nullable=False)
    country = relationship("CountryModel", backref="states")


class CityModel(Base, IDMixin, TimestampMixin, SoftDeleteMixin, NameMixin):
    __tablename__ = "cities"
    state_id = Column(String(36), ForeignKey("states.id"), nullable=False)
    state = relationship("StateModel", backref="cities")
