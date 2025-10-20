import os
import random
from datetime import datetime
import string
from uuid import uuid4
from fastapi import HTTPException, status
import phonenumbers
from sqlalchemy import inspect
from jwcrypto import jwk, jwt
from app.config import JWT_KEY
import json
import bcrypt

def now():
    return datetime.now()


def generate_id():
    id = str(uuid4())
    return id


def generate_otp():
    otp = ""
    while len(otp) < 6:
        otp += str(random.randint(0, 9))
    return otp


def date_time_diff_min(start: datetime, end: datetime):
    duration = end - start
    duration_in_seconds = duration.total_seconds()
    minutes = divmod(duration_in_seconds, 60)[0]
    return minutes


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def check_number(number):
    try:
        number = str(number)
        number = phonenumbers.parse(number, "IN")
        number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        return number
    except Exception as e:
        print(e)
        return False

def remove_file(path):
    os.remove(path)


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_OTP(length=6):
    characters = string.ascii_letters + string.digits  # Includes letters and digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_password(length=8):
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    # Define the character sets for the password
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits

    # Ensure the password contains at least one lowercase, one uppercase, one digit, and one special character
    password = [
        random.choice(lowercase),  # Add a lowercase letter
        random.choice(uppercase),  # Add an uppercase letter
        random.choice(digits),  # Add a digit
    ]

    # Add random characters to fill the remaining length
    all_characters = lowercase + uppercase + digits 
    password += random.choices(all_characters, k=length - 4)

    # Shuffle the password to ensure randomness
    random.shuffle(password)

    # Return the password as a string
    return "".join(password)


def change_date_format(date: datetime) -> str:
    formatted_date = date.strftime("%d %b %Y")
    return formatted_date


def get_token(admin_user_id, email, type):
    claims = {"id": admin_user_id, "email": email,"type": type, "time": str(now())}

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

def validate_token(token: str) -> dict:
    try:
        key = jwk.JWK(**JWT_KEY)
        
        # Decrypt the outer JWE
        outer = jwt.JWT(key=key, jwt=token, expected_type="JWE")
        # Decode the inner signed JWT
        inner = jwt.JWT(key=key, jwt=outer.claims)
        claims = json.loads(inner.claims)

        return claims

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

def get_user_type(token: str) -> str:
    claims = validate_token(token)
    return claims.get("type")

def create_password(password: str) -> str:
    password = password.encode("utf-8")
    password = bcrypt.hashpw(password, bcrypt.gensalt(4))
    password = password.decode("utf-8")
    return password

def generate_order_code():
    return "ORD-" + datetime.now().strftime("%Y%m%d%H%M%S")
