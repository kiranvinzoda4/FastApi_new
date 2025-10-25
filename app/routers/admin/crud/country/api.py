import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.security import get_current_user
from app.middleware.rate_limit import limiter
from . import crud, schemas

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/countries", tags=["Countries"])

@router.get(
    "/",
    response_model=schemas.CountryList,
    summary="Get all countries",
    description="Retrieve a paginated list of countries with optional search and sorting"
)
@limiter.limit("30/minute")
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
    try:
        result = crud.get_countries(
            db=db,
            start=start,
            limit=limit,
            search=search,
            sort_by=sort_by,
            order=order
        )
        logger.info(f"Retrieved {len(result['list'])} countries for user {current_user.get('sub')}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving countries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve countries"
        )

@router.get(
    "/{country_id}",
    response_model=schemas.Country,
    summary="Get country by ID",
    description="Retrieve a specific country by its ID"
)
@limiter.limit("60/minute")
async def get_country(
    request,
    country_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific country by ID"""
    try:
        country = crud.get_country_by_id(db, country_id)
        logger.info(f"Retrieved country {country_id} for user {current_user.get('sub')}")
        return country
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving country {country_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve country"
        )

@router.post(
    "/",
    response_model=schemas.Country,
    status_code=status.HTTP_201_CREATED,
    summary="Create new country",
    description="Create a new country with unique code"
)
@limiter.limit("10/minute")
async def create_country(
    request,
    country: schemas.CountryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new country"""
    try:
        new_country = crud.create_country(db=db, country=country)
        logger.info(f"Created country {new_country.id} by user {current_user.get('sub')}")
        return new_country
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating country: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create country"
        )

@router.put(
    "/{country_id}",
    response_model=schemas.Country,
    summary="Update country",
    description="Update an existing country"
)
@limiter.limit("10/minute")
async def update_country(
    request,
    country_id: str,
    country: schemas.CountryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing country"""
    try:
        updated_country = crud.update_country(db=db, country_id=country_id, country=country)
        logger.info(f"Updated country {country_id} by user {current_user.get('sub')}")
        return updated_country
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating country {country_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update country"
        )

@router.delete(
    "/{country_id}",
    summary="Delete country",
    description="Soft delete a country (mark as deleted)"
)
@limiter.limit("5/minute")
async def delete_country(
    request,
    country_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a country (soft delete)"""
    try:
        result = crud.delete_country(db=db, country_id=country_id)
        logger.info(f"Deleted country {country_id} by user {current_user.get('sub')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting country {country_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete country"
        )