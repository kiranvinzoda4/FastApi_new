import json
import traceback
import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jwcrypto import jwk, jwt
from app.config import JWT_KEY
from app.libs.utils import now, create_password, generate_otp
from app.models import AdminUserModel
from .schemas import LoginRequest, LoginResponse, Profile, ChangePassword, ForgotPasswordRequest, OTPVerifyRequest, ResetPasswordRequest
# Import functions that were in the old auth.py - need to be implemented or moved
# from app.routers.admin.crud.auth import generate_access_token, generate_refresh_token, refresh_access_token
from app.libs.emails import send_email
from app.libs.email_template import forgot_password_template


def verify_token(db: Session, token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token"
        )

    try:
        key = jwk.JWK(**JWT_KEY)
        ET = jwt.JWT(key=key, jwt=token, expected_type="JWE")
        ST = jwt.JWT(key=key, jwt=ET.claims)
        claims = json.loads(ST.claims)

        db_admin_user = get_admin_user_by_id(db, id=claims["id"])

        if db_admin_user is None or db_admin_user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found."
            )

        return db_admin_user

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


def get_admin_user_by_id(db: Session, id: str):
    return db.query(AdminUserModel).filter(AdminUserModel.id == id, AdminUserModel.is_deleted == False).first()


def get_admin_user_by_email(db: Session, email: str):
    return (
        db.query(AdminUserModel)
        .filter(AdminUserModel.email == email, AdminUserModel.is_deleted == False)
        .first()
    )


def get_admin_user_by_otp(db: Session, otp: str):
    return (
        db.query(AdminUserModel)
        .filter(AdminUserModel.otp == otp, AdminUserModel.is_deleted == False)
        .first()
    )


def sign_in(db: Session, admin_user: LoginRequest) -> LoginResponse:
    db_admin_user = get_admin_user_by_email(db, email=admin_user.email)

    if db_admin_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    elif db_admin_user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deleted")

    hashed = db_admin_user.password.encode("utf-8")
    password = admin_user.password.encode("utf-8")

    if not bcrypt.checkpw(password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # TODO: Implement token generation functions
    db_admin_user.token = "temp_token"  # generate_access_token(db_admin_user.id, db_admin_user.email)
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
    db_admin_user = get_admin_user_by_email(db=db, email=request.email)
    if not db_admin_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User Not Found.')

    otp = generate_otp()
    db_admin_user.otp = otp
    db.commit()

    email_body = forgot_password_template(
        first_name=db_admin_user.first_name,
        last_name=db_admin_user.last_name,
        otp=otp
    )

    if not send_email(
        recipients=[db_admin_user.email],
        subject="DailyVeg: OTP for Password Reset",
        html_body=email_body 
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while sending email.",
        )

    return {"detail": "OTP has been sent successfully."}


def otp_verify(db: Session, request: OTPVerifyRequest):
    db_admin_user = get_admin_user_by_otp(db=db, otp=request.otp)
    if not db_admin_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='User Not Found, try again.')
    db_admin_user.user_type = request.user_type
    db.commit()
    return db_admin_user


def reset_password(db: Session, request: ResetPasswordRequest):
    db_admin_user = get_admin_user_by_email(db=db, email=request.email)
    if not db_admin_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if db_admin_user.otp != request.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP.")

    db_admin_user.password = create_password(request.new_password)
    db_admin_user.otp = None
    db_admin_user.updated_at = now()
    db.commit()

    return db_admin_user