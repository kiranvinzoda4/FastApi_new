from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.admin.crud.auth_mod import crud
from app.routers.admin.crud.auth_mod.schemas import (
    LoginRequest,
    LoginResponse,
    Profile,
    ChangePassword,
    ForgotPasswordRequest,
    OTPVerifyRequest,
    ResetPasswordRequest,
    ResetPasswordWithTokenRequest,
    VerifyResetTokenRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse, summary="User login", description="POST /auth/login - Admin user login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    return crud.sign_in(db, request)


@router.put("/profile", summary="Update profile", description="PUT /auth/profile - Update admin user profile")
async def update_profile(request: Profile, token: str, db: Session = Depends(get_db)):
    return crud.update_profile(db, request, token)


@router.put("/change-password", summary="Change password", description="PUT /auth/change-password - Change admin user password")
async def change_password(
    request: ChangePassword, token: str, db: Session = Depends(get_db)
):
    return crud.change_password(db, request, token)


@router.post("/forgot-password", summary="Forgot password (legacy)", description="POST /auth/forgot-password - Send OTP for password reset (legacy)")
async def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    return crud.send_forgot_password_email(db, request)


@router.post("/forgot-password-link", summary="Forgot password link", description="POST /auth/forgot-password-link - Send secure password reset link")
async def forgot_password_link(
    request: ForgotPasswordRequest, http_request: Request, db: Session = Depends(get_db)
):
    # Get base URL from request
    base_url = f"{http_request.url.scheme}://{http_request.url.netloc}"
    return crud.send_password_reset_link(db, request, base_url)


@router.post("/verify-otp")
async def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP (legacy)"""
    return crud.otp_verify(db, request)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with OTP (legacy)"""
    return crud.reset_password(db, request)


@router.post("/verify-reset-token")
async def verify_reset_token(
    request: VerifyResetTokenRequest, db: Session = Depends(get_db)
):
    """Verify reset token validity"""
    user = crud.verify_reset_token_and_get_user(db, request.token)
    return {
        "valid": True,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@router.post("/reset-password-with-token")
async def reset_password_with_token(
    request: ResetPasswordWithTokenRequest, db: Session = Depends(get_db)
):
    """Reset password using secure token"""
    return crud.reset_password_with_token(db, request.token, request.new_password)
