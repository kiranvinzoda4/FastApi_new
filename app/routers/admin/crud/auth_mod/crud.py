import json
import traceback
import logging
import bcrypt
import hashlib
import re
import secrets
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jwcrypto import jwk, jwt
from app.config import JWT_KEY
from app.libs.utils import now, create_password, generate_otp
from app.models import AdminUserModel
from .schemas import (
    LoginRequest,
    LoginResponse,
    Profile,
    ChangePassword,
    ForgotPasswordRequest,
    OTPVerifyRequest,
    ResetPasswordRequest,
)

# Import functions that were in the old auth.py - need to be implemented or moved
# from app.routers.admin.crud.auth import generate_access_token, generate_refresh_token, refresh_access_token
from app.libs.emails import send_email
from app.libs.template_manager import (
    forgot_password_template,
    password_reset_link_template,
)

logger = logging.getLogger(__name__)
# OTP Configuration
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
MAX_GENERATION_ATTEMPTS = 3
RATE_LIMIT_HOURS = 1
# Reset Token Configuration
RESET_TOKEN_EXPIRY_MINUTES = 30
RESET_TOKEN_LENGTH = 32


def hash_otp(otp: str) -> str:
    """Hash OTP for secure storage"""
    try:
        return hashlib.sha256(otp.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Error hashing OTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process OTP",
        )


def verify_otp_hash(otp: str, hashed_otp: str) -> bool:
    """Verify OTP against stored hash"""
    return hashlib.sha256(otp.encode()).hexdigest() == hashed_otp


def validate_otp_format(otp: str) -> bool:
    """Validate OTP format (6 digits)"""
    return bool(re.match(r"^\d{6}$", otp))


def is_rate_limited(user: AdminUserModel) -> bool:
    """Check if user is rate limited for OTP generation"""
    if not user.otp_generated_at:
        return False
    time_diff = now() - user.otp_generated_at
    if time_diff < timedelta(hours=RATE_LIMIT_HOURS):
        return (user.otp_generation_count or 0) >= MAX_GENERATION_ATTEMPTS
    return False


def is_otp_expired(user: AdminUserModel) -> bool:
    """Check if OTP is expired"""
    if not user.otp_expires_at:
        return True
    return now() > user.otp_expires_at


def generate_reset_token() -> str:
    """Generate cryptographically secure reset token"""
    return secrets.token_urlsafe(RESET_TOKEN_LENGTH)


def hash_reset_token(token: str) -> str:
    """Hash reset token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_reset_token(token: str, hashed_token: str) -> bool:
    """Verify reset token against stored hash"""
    return hashlib.sha256(token.encode()).hexdigest() == hashed_token


def is_reset_token_expired(user: AdminUserModel) -> bool:
    """Check if reset token is expired"""
    if not user.reset_token_expires_at:
        return True
    return now() > user.reset_token_expires_at


def verify_token(db: Session, token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token"
        )
    try:
        key = jwk.JWK(**JWT_KEY)
        ET = jwt.JWT(key=key, jwt=token, expected_type="JWE")
        ST = jwt.JWT(key=key, jwt=ET.claims)
        claims = json.loads(ST.claims)
        db_admin_user = get_admin_user_by_id(db, id=claims["id"])
        if db_admin_user is None or db_admin_user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found."
            )
        return db_admin_user
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


def get_admin_user_by_id(db: Session, id: str):
    try:
        return (
            db.query(AdminUserModel)
            .filter(AdminUserModel.id == id, AdminUserModel.is_deleted.is_(False))
            .first()
        )
    except Exception as e:
        logger.error(f"Database error in get_admin_user_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


def get_admin_user_by_email(db: Session, email: str):
    try:
        return (
            db.query(AdminUserModel)
            .filter(AdminUserModel.email == email, AdminUserModel.is_deleted.is_(False))
            .first()
        )
    except Exception as e:
        logger.error(f"Database error in get_admin_user_by_email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


def get_admin_user_by_email_with_otp(db: Session, email: str) -> AdminUserModel:
    """Get user by email for OTP operations"""
    try:
        return (
            db.query(AdminUserModel)
            .filter(AdminUserModel.email == email, AdminUserModel.is_deleted.is_(False))
            .first()
        )
    except Exception as e:
        logger.error(f"Database error in get_admin_user_by_email_with_otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )


def sign_in(db: Session, admin_user: LoginRequest) -> LoginResponse:
    db_admin_user = get_admin_user_by_email(db, email=admin_user.email)
    if db_admin_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    elif db_admin_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deleted"
        )
    hashed = db_admin_user.password.encode("utf-8")
    password = admin_user.password.encode("utf-8")
    if not bcrypt.checkpw(password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    # TODO: Implement token generation functions
    db_admin_user.token = (
        "temp_token"  # generate_access_token(db_admin_user.id, db_admin_user.email)
    )
    db_admin_user.refresh_token = "temp_refresh_token"  # generate_refresh_token(db_admin_user.id, db_admin_user.email)
    return db_admin_user


def update_profile(db: Session, admin_user: Profile, token: str):
    db_admin_user = verify_token(db, token=token)
    db_admin_user.first_name = admin_user.first_name
    db_admin_user.last_name = admin_user.last_name
    db_admin_user.email = admin_user.email
    db_admin_user.phone = admin_user.phone
    db_admin_user.updated_at = now()
    db.commit()
    return db_admin_user


def change_password(db: Session, admin_user: ChangePassword, token: str):
    db_admin_user = verify_token(db, token=token)
    try:
        hashed = bytes(db_admin_user.password, "utf-8")
        password = bytes(admin_user.old_password, "utf-8")
        result = bcrypt.checkpw(password, hashed)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect old password"
        )
    password = create_password(admin_user.new_password)
    db_admin_user.password = password
    db_admin_user.updated_at = now()
    db.commit()
    return db_admin_user


def send_forgot_password_email(db: Session, request: ForgotPasswordRequest):
    try:
        db_admin_user = get_admin_user_by_email(db=db, email=request.email)
        if not db_admin_user:
            logger.warning(
                f"Password reset attempt for non-existent email: {request.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found."
            )
        # Check rate limiting
        if is_rate_limited(db_admin_user):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many OTP requests. Try again after {RATE_LIMIT_HOURS} hour(s).",
            )
        # Generate secure OTP
        otp = generate_otp()
        current_time = now()
        # Update rate limiting counters
        if (
            db_admin_user.otp_generated_at
            and current_time - db_admin_user.otp_generated_at
            < timedelta(hours=RATE_LIMIT_HOURS)
        ):
            db_admin_user.otp_generation_count = (
                db_admin_user.otp_generation_count or 0
            ) + 1
        else:
            db_admin_user.otp_generation_count = 1
        # Store hashed OTP with expiration
        db_admin_user.otp = hash_otp(otp)
        db_admin_user.otp_generated_at = current_time
        db_admin_user.otp_expires_at = current_time + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        )
        db_admin_user.otp_attempts = 0
        db_admin_user.updated_at = current_time
        db.commit()
        logger.info(f"OTP generated for user: {db_admin_user.email}")
        email_body = forgot_password_template(
            first_name=db_admin_user.first_name,
            last_name=db_admin_user.last_name,
            otp=otp,  # Send plain OTP in email
        )
        if not send_email(
            recipients=[db_admin_user.email],
            subject="DailyVeg: OTP for Password Reset",
            html_body=email_body,
        ):
            logger.error(
                f"Failed to send password reset email to: {db_admin_user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while sending email.",
            )
        logger.info(f"Password reset email sent successfully to: {db_admin_user.email}")
        return {
            "detail": f"OTP has been sent successfully. Valid for {OTP_EXPIRY_MINUTES} minutes."
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in send_forgot_password_email: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    except Exception as e:
        logger.error(f"Unexpected error in send_forgot_password_email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def otp_verify(db: Session, request: OTPVerifyRequest):
    # Validate OTP format
    if not validate_otp_format(request.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP format. Must be 6 digits.",
        )
    # This function needs email in request to work properly
    # For now, we'll search by OTP hash (less secure but maintains compatibility)
    otp_hash = hash_otp(request.otp)
    try:
        db_admin_user = (
            db.query(AdminUserModel)
            .filter(
                AdminUserModel.otp == otp_hash, AdminUserModel.is_deleted.is_(False)
            )
            .first()
        )
        if not db_admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP or OTP expired.",
            )
        # Check expiration
        if is_otp_expired(db_admin_user):
            # Clear expired OTP
            db_admin_user.otp = None
            db_admin_user.otp_expires_at = None
            db_admin_user.otp_attempts = 0
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one.",
            )
        # Check attempt limit
        if (db_admin_user.otp_attempts or 0) >= MAX_OTP_ATTEMPTS:
            # Clear OTP after max attempts
            db_admin_user.otp = None
            db_admin_user.otp_expires_at = None
            db_admin_user.otp_attempts = 0
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many verification attempts. Please request a new OTP.",
            )
        # OTP is valid - clear it immediately
        db_admin_user.otp = None
        db_admin_user.otp_expires_at = None
        db_admin_user.otp_attempts = 0
        db_admin_user.user_type = request.user_type
        db_admin_user.updated_at = now()
        db.commit()
        logger.info(f"OTP verified successfully for user: {db_admin_user.email}")
        return db_admin_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in otp_verify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OTP verification failed",
        )


def reset_password(db: Session, request: ResetPasswordRequest):
    # Validate OTP format
    if not validate_otp_format(request.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP format. Must be 6 digits.",
        )
    db_admin_user = get_admin_user_by_email(db=db, email=request.email)
    if not db_admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    # Check if OTP exists
    if not db_admin_user.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP found. Please request a new one.",
        )
    # Check expiration
    if is_otp_expired(db_admin_user):
        # Clear expired OTP
        db_admin_user.otp = None
        db_admin_user.otp_expires_at = None
        db_admin_user.otp_attempts = 0
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one.",
        )
    # Check attempt limit
    if (db_admin_user.otp_attempts or 0) >= MAX_OTP_ATTEMPTS:
        # Clear OTP after max attempts
        db_admin_user.otp = None
        db_admin_user.otp_expires_at = None
        db_admin_user.otp_attempts = 0
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many verification attempts. Please request a new OTP.",
        )
    # Verify OTP
    if not verify_otp_hash(request.otp, db_admin_user.otp):
        # Increment attempt counter
        db_admin_user.otp_attempts = (db_admin_user.otp_attempts or 0) + 1
        db.commit()
        remaining_attempts = MAX_OTP_ATTEMPTS - db_admin_user.otp_attempts
        if remaining_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many verification attempts. Please request a new OTP.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining_attempts} attempts remaining.",
        )
    # OTP is valid - reset password and clear OTP
    db_admin_user.password = create_password(request.new_password)
    db_admin_user.otp = None
    db_admin_user.otp_expires_at = None
    db_admin_user.otp_attempts = 0
    db_admin_user.updated_at = now()
    db.commit()
    logger.info(f"Password reset successfully for user: {db_admin_user.email}")
    return db_admin_user


def send_password_reset_link(
    db: Session, request: ForgotPasswordRequest, base_url: str
):
    """Send secure password reset link via email"""
    try:
        db_admin_user = get_admin_user_by_email(db=db, email=request.email)
        if not db_admin_user:
            logger.warning(
                f"Password reset attempt for non-existent email: {request.email}"
            )
            # Don't reveal if email exists or not for security
            return {"detail": "If the email exists, a reset link has been sent."}
        # Check rate limiting
        if is_rate_limited(db_admin_user):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many reset requests. Try again after {RATE_LIMIT_HOURS} hour(s).",
            )
        # Generate secure reset token
        reset_token = generate_reset_token()
        current_time = now()
        # Update rate limiting counters
        if (
            db_admin_user.otp_generated_at
            and current_time - db_admin_user.otp_generated_at
            < timedelta(hours=RATE_LIMIT_HOURS)
        ):
            db_admin_user.otp_generation_count = (
                db_admin_user.otp_generation_count or 0
            ) + 1
        else:
            db_admin_user.otp_generation_count = 1
        # Store hashed reset token
        db_admin_user.reset_token = hash_reset_token(reset_token)
        db_admin_user.reset_token_expires_at = current_time + timedelta(
            minutes=RESET_TOKEN_EXPIRY_MINUTES
        )
        db_admin_user.reset_token_used = False
        db_admin_user.otp_generated_at = current_time
        db_admin_user.updated_at = current_time
        db.commit()
        # Create reset link
        reset_link = f"{base_url}/reset-password?token={reset_token}"
        logger.info(f"Reset token generated for user: {db_admin_user.email}")
        # Send reset link email
        email_body = password_reset_link_template(
            first_name=db_admin_user.first_name,
            last_name=db_admin_user.last_name,
            reset_link=reset_link,
            expiry_minutes=RESET_TOKEN_EXPIRY_MINUTES,
        )
        if not send_email(
            recipients=[db_admin_user.email],
            subject="Password Reset Request - Secure Link",
            html_body=email_body,
        ):
            logger.error(
                f"Failed to send password reset email to: {db_admin_user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error while sending email.",
            )
        logger.info(f"Password reset link sent successfully to: {db_admin_user.email}")
        return {
            "detail": f"Password reset link has been sent to your email. Valid for {RESET_TOKEN_EXPIRY_MINUTES} minutes."
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in send_password_reset_link: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    except Exception as e:
        logger.error(f"Unexpected error in send_password_reset_link: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


def verify_reset_token_and_get_user(db: Session, token: str) -> AdminUserModel:
    """Verify reset token and return user if valid"""
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token is required",
            )
        # Hash the provided token to compare with stored hash
        token_hash = hash_reset_token(token)
        # Find user with this token
        db_admin_user = (
            db.query(AdminUserModel)
            .filter(
                AdminUserModel.reset_token == token_hash,
                AdminUserModel.is_deleted.is_(False),
            )
            .first()
        )
        if not db_admin_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        # Check if token is expired
        if is_reset_token_expired(db_admin_user):
            # Clear expired token
            db_admin_user.reset_token = None
            db_admin_user.reset_token_expires_at = None
            db_admin_user.reset_token_used = False
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired. Please request a new one.",
            )
        # Check if token was already used
        if db_admin_user.reset_token_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has already been used. Please request a new one.",
            )
        return db_admin_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying reset token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed",
        )


def reset_password_with_token(db: Session, token: str, new_password: str):
    """Reset password using secure token"""
    try:
        # Verify token and get user
        db_admin_user = verify_reset_token_and_get_user(db, token)
        # Reset password
        db_admin_user.password = create_password(new_password)
        # Mark token as used and clear it
        db_admin_user.reset_token = None
        db_admin_user.reset_token_expires_at = None
        db_admin_user.reset_token_used = True
        db_admin_user.updated_at = now()
        db.commit()
        logger.info(
            f"Password reset successfully using token for user: {db_admin_user.email}"
        )
        return {
            "detail": "Password has been reset successfully. You can now login with your new password."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password with token: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )
