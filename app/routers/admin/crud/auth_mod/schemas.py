from typing import List
from pydantic import BaseModel, Field, model_validator
from fastapi import HTTPException, status
from app.routers.admin.crud.schemas import EmailMixin, IDMixin, PhoneMixin, PasswordMixin, UserTypeMixin, ListResponseMixin


class LoginRequest(EmailMixin):
    password: str = Field(min_length=6, max_length=50)


class LoginResponse(EmailMixin, IDMixin):
    first_name: str
    last_name: str
    token: str
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ProfileUpdate(EmailMixin, PhoneMixin):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class Profile(ProfileUpdate, IDMixin):
    pass


class ChangePassword(BaseModel):
    old_password: str = Field(min_length=8, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)
    conform_new_password: str = Field(min_length=8, max_length=255)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.conform_new_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New password and confirm password do not match.",
            )
        return self


class ForgotPasswordRequest(EmailMixin, UserTypeMixin):
    pass


class OTPVerifyRequest(UserTypeMixin):
    otp: str


class OTPVerifyResponse(OTPVerifyRequest, EmailMixin):
    pass


class ResetPasswordRequest(OTPVerifyResponse, PasswordMixin):
    pass


class APILogItem(BaseModel):
    id: str
    url: str
    method: str
    payload: str | None
    status_code: int
    error_message: str | None
    created_at: str


class APILogList(ListResponseMixin):
    list: List[APILogItem]