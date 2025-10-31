from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.libs.utils import get_user_type

# Import error_logs functions - need to be implemented
# from app.routers.admin.crud import error_logs
from .schemas import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    Profile,
    ProfileUpdate,
    ChangePassword,
    ForgotPasswordRequest,
    OTPVerifyRequest,
    OTPVerifyResponse,
    ResetPasswordRequest,
    APILogList,
)
from . import crud

router = APIRouter()


@router.post(
    "/admin-login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    tags=["Authentication"],
)
def admin_login(admin_user: LoginRequest, db: Session = Depends(get_db)):
    return crud.sign_in(db, admin_user)


@router.post(
    "/refresh-access-token",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    tags=["Authentication"],
)
def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    # TODO: Implement refresh_access_token function
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/admin-profile", response_model=Profile, tags=["Profile"])
def get_admin_profile(token: str = Header(None), db: Session = Depends(get_db)):
    return crud.verify_token(db, token=token)


@router.put("/admin-profile", response_model=Profile, tags=["Profile"])
def update_admin_profile(
    admin_user: ProfileUpdate, token: str = Header(None), db: Session = Depends(get_db)
):
    return crud.update_profile(db, admin_user=admin_user, token=token)


@router.put("/admin-change-password", tags=["Profile"])
def change_admin_password(
    admin_user: ChangePassword, token: str = Header(None), db: Session = Depends(get_db)
):
    crud.verify_token(db, token=token)
    crud.change_password(db, admin_user=admin_user, token=token)
    return {"detail": "Password changed successfully."}


@router.put("/send-forgot-password-email", tags=["Profile"])
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return crud.send_forgot_password_email(db, request=request)


@router.put(
    "/forgot-password-otp-verify", response_model=OTPVerifyResponse, tags=["Profile"]
)
def otp_verify(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    return crud.otp_verify(db, request=request)


@router.put("/reset-password", response_model=Profile, tags=["Profile"])
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return crud.reset_password(db, request=request)

