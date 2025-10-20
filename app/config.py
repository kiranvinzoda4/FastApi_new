import json
import os
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")
JWT_KEY = os.environ.get("JWT_KEY")
REFRESH_JWT_KEY = os.environ.get("REFRESH_JWT_KEY")
ACCESS_JWT_KEY = os.environ.get("ACCESS_JWT_KEY")

if JWT_KEY:
    try:
        JWT_KEY = json.loads(JWT_KEY)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT key"
        )
else:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWT key not set"
    )


if ACCESS_JWT_KEY:
    try:
        ACCESS_JWT_KEY = json.loads(ACCESS_JWT_KEY)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access JWT key"
        )
else:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Access JWT key not set"
    )

if REFRESH_JWT_KEY:
    try:
        REFRESH_JWT_KEY = json.loads(REFRESH_JWT_KEY)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh JWT key"
        )
else:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=" Refresh JWT key not set"
    )