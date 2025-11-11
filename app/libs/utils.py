import os
import random
import secrets
from datetime import datetime, timezone
import string
from uuid import uuid4
from typing import Dict, Any, Optional, Union, List
from fastapi import HTTPException, status
import phonenumbers
from sqlalchemy import inspect
from jwcrypto import jwk, jwt
from app.config import JWT_KEY
import json
import bcrypt
import logging

logger = logging.getLogger(__name__)


def now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


def generate_id() -> str:
    """Generate unique UUID string"""
    return str(uuid4())


def generate_otp(length: int = 6) -> str:
    """Generate secure numeric OTP"""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def date_time_diff_min(start: datetime, end: datetime) -> float:
    duration = end - start
    duration_in_seconds = duration.total_seconds()
    minutes = divmod(duration_in_seconds, 60)[0]
    return minutes


def object_as_dict(obj: Any) -> Dict[str, Any]:
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def check_number(number: Optional[Union[str, int]]) -> Union[str, bool]:
    try:
        if not number:
            return False
        number_str = str(number)
        parsed_number = phonenumbers.parse(number_str, "IN")
        formatted_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )
        return formatted_number
    except Exception as e:
        logger.error(f"Phone number validation error: {e}")
        return False


def remove_file(path: str) -> None:
    os.remove(path)


def generate_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


# generate_OTP function removed - use generate_otp() instead
def generate_password(length: int = 8) -> str:
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")
    # Define the character sets for the password
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    # Ensure the password contains at least one lowercase, one uppercase, one digit
    password: List[str] = [
        random.choice(lowercase),  # Add a lowercase letter
        random.choice(uppercase),  # Add an uppercase letter
        random.choice(digits),  # Add a digit
    ]
    # Add random characters to fill the remaining length
    all_characters = lowercase + uppercase + digits
    password += random.choices(all_characters, k=length - 3)
    # Shuffle the password to ensure randomness
    random.shuffle(password)
    # Return the password as a string
    return "".join(password)


def change_date_format(date: datetime) -> str:
    formatted_date = date.strftime("%d %b %Y")
    return formatted_date


def get_token(admin_user_id: str, email: str, user_type: str) -> str:
    claims = {
        "id": admin_user_id,
        "email": email,
        "type": user_type,
        "time": str(now()),
    }
    # Create a signed token with the generated key
    key = jwk.JWK(**JWT_KEY)
    token = jwt.JWT(header={"alg": "HS256"}, claims=claims)
    token.make_signed_token(key)
    # Further encrypt the token with the same key
    encrypted_token = jwt.JWT(
        header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=token.serialize()
    )
    encrypted_token.make_encrypted_token(key)
    return encrypted_token.serialize()


def validate_token(token: str) -> Dict[str, Any]:
    try:
        if not token or not isinstance(token, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format"
            )
        key = jwk.JWK(**JWT_KEY)
        # Decrypt the outer JWE
        outer = jwt.JWT(key=key, jwt=token, expected_type="JWE")
        # Decode the inner signed JWT
        inner = jwt.JWT(key=key, jwt=outer.claims)
        claims: Dict[str, Any] = json.loads(inner.claims)
        return claims
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token."
        )


def get_user_type(token: str) -> str:
    claims = validate_token(token)
    return claims.get("type")


def create_password(password: str) -> str:
    password = password.encode("utf-8")
    password = bcrypt.hashpw(password, bcrypt.gensalt(4))
    password = password.decode("utf-8")
    return password


def generate_order_code() -> str:
    """Generate unique order code with UTC timestamp"""
    return "ORD-" + now().strftime("%Y%m%d%H%M%S")
