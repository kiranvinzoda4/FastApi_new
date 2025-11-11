from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user
from . import crud, schemas

router = APIRouter(prefix="/countries", tags=["Countries"])


def admin_auth(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return db


@router.get(
    "/",
    response_model=schemas.CountryList,
    summary="Get all countries",
    description="GET /countries - Retrieve a paginated list of countries with optional search and sorting",
)
async def get_countries(
    start: int = Query(0, ge=0, description="Starting index for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    search: Optional[str] = Query(
        None, max_length=50, description="Search term for country name or code"
    ),
    sort_by: Optional[str] = Query(None, max_length=50, description="Field to sort by"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(admin_auth),
) -> schemas.CountryList:
    return crud.get_countries(
        db=db, start=start, limit=limit, search=search, sort_by=sort_by, order=order
    )


@router.get(
    "/{country_id}",
    response_model=schemas.Country,
    summary="Get country by ID",
    description="GET /countries/{id} - Retrieve a specific country by its ID",
)
async def get_country(
    country_id: str = Path(
        ..., min_length=36, max_length=36, description="Country ID"
    ),
    db: Session = Depends(admin_auth),
) -> schemas.Country:
    return crud.get_country_by_id(db, country_id)


@router.post(
    "/",
    response_model=schemas.Country,
    status_code=status.HTTP_201_CREATED,
    summary="Create new country",
    description="POST /countries - Create a new country with unique code",
)
async def create_country(
    country: schemas.CountryCreate, db: Session = Depends(admin_auth)
) -> schemas.Country:
    return crud.create_country(db=db, country=country)


@router.put(
    "/{country_id}",
    response_model=schemas.Country,
    summary="Update country",
    description="PUT /countries/{id} - Update an existing country",
)
async def update_country(
    country_id: str = Path(
        ..., min_length=36, max_length=36, description="Country ID"
    ),
    country: schemas.CountryUpdate = ...,
    db: Session = Depends(admin_auth),
) -> schemas.Country:
    return crud.update_country(db=db, country_id=country_id, country=country)


@router.delete(
    "/{country_id}",
    summary="Delete country",
    description="DELETE /countries/{id} - Soft delete a country (mark as deleted)",
)
async def delete_country(
    country_id: str = Path(
        ..., min_length=36, max_length=36, description="Country ID"
    ),
    db: Session = Depends(admin_auth),
) -> Dict[str, str]:
    return crud.delete_country(db=db, country_id=country_id)