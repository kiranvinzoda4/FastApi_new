from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.security import get_current_user
from . import crud, schemas
router = APIRouter(prefix="/countries", tags=["Countries"])

@router.get(
    "/",
    response_model=schemas.CountryList,
    summary="Get all countries",
    description="Retrieve a paginated list of countries with optional search and sorting"
)
async def get_countries(
    request,
    start: int = Query(0, ge=0, description="Starting index for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    search: Optional[str] = Query(None, description="Search term for country name or code"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of countries with search and sorting capabilities"""
    return crud.get_countries(
        db=db,
        start=start,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order
    )

@router.get(
    "/{country_id}",
    response_model=schemas.Country,
    summary="Get country by ID",
    description="Retrieve a specific country by its ID"
)
async def get_country(
    request,
    country_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific country by ID"""
    return crud.get_country_by_id(db, country_id)

@router.post(
    "/",
    response_model=schemas.Country,
    status_code=status.HTTP_201_CREATED,
    summary="Create new country",
    description="Create a new country with unique code"
)
async def create_country(
    request,
    country: schemas.CountryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new country"""
    return crud.create_country(db=db, country=country)

@router.put(
    "/{country_id}",
    response_model=schemas.Country,
    summary="Update country",
    description="Update an existing country"
)
async def update_country(
    request,
    country_id: str,
    country: schemas.CountryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing country"""
    return crud.update_country(db=db, country_id=country_id, country=country)

@router.delete(
    "/{country_id}",
    summary="Delete country",
    description="Soft delete a country (mark as deleted)"
)
async def delete_country(
    request,
    country_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a country (soft delete)"""
    return crud.delete_country(db=db, country_id=country_id)