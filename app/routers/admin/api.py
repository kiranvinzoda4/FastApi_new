from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session
from app.libs.utils import get_user_type
from app.dependencies import get_db

from app.routers.admin.crud.auth_mod.api import router as auth_router
from app.routers.admin.crud.country.api import router as country_router
from app.routers.admin.crud.state.api import router as state_router
from app.routers.admin.crud.city.api import router as city_router

router = APIRouter()

# Include module routers
router.include_router(auth_router)
router.include_router(country_router)
router.include_router(state_router)
router.include_router(city_router)





