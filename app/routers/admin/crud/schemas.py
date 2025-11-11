from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime


class IDMixin(BaseModel):
    id: str = Field(min_length=36, max_length=36)


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class NameMixin(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class EmailMixin(BaseModel):
    email: str = Field(min_length=6, max_length=200)


class PhoneMixin(BaseModel):
    phone: str = Field(min_length=10, max_length=15)


class PasswordMixin(BaseModel):
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


class UserTypeMixin(BaseModel):
    user_type: int = Field(3, description="3 for Admin")


class ListResponseMixin(BaseModel):
    count: int
    model_config = ConfigDict(from_attributes=True)


class EntityMixin(IDMixin, TimestampMixin):
    model_config = ConfigDict(from_attributes=True)
