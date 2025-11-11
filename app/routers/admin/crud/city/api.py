from fastapi import APIRouter, Query, Depends, HTTPException, status
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user
from . import crud, schemas

router = APIRouter()


def admin_auth(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    """Token validation dependency."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return db


@router.get("/cities", response_model=schemas.CityList, tags=["Cities"])
async def get_cities(
    start: int = Query(0, ge=0, description="Starting offset"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    sort_by: Optional[str] = Query(None, max_length=50),
    order: Optional[str] = Query(None, regex="^(asc|desc)$", description="asc | desc"),
    search: Optional[str] = Query(None, max_length=50),
    state_id: Optional[str] = Query(None, description="Filter by state ID"),
    country_id: Optional[str] = Query(None, description="Filter by country ID"),
    db: Session = Depends(admin_auth),
) -> schemas.CityList:
    return crud.get_cities(
        db, start, limit, sort_by, order, search, state_id, country_id
    )


@router.get("/cities/{city_id}", response_model=schemas.CityWithState, tags=["Cities"])
async def get_city(
    city_id: str = Query(..., min_length=36, max_length=36, description="City ID"),
    db: Session = Depends(admin_auth),
) -> schemas.CityWithState:
    return crud.get_city_by_id(db, city_id)


@router.post("/cities", response_model=schemas.CityWithState, tags=["Cities"])
async def create_city(
    city_data: schemas.CityCreate, db: Session = Depends(admin_auth)
) -> schemas.CityWithState:
    return crud.create_city(db, city_data)


@router.put("/cities/{city_id}", response_model=schemas.CityWithState, tags=["Cities"])
async def update_city(
    city_id: str = Query(..., min_length=36, max_length=36, description="City ID"),
    city_data: schemas.CityUpdate = ...,
    db: Session = Depends(admin_auth),
) -> schemas.CityWithState:
    return crud.update_city(db, city_id, city_data)


@router.delete("/cities/{city_id}", tags=["Cities"])
async def delete_city(
    city_id: str = Query(..., min_length=36, max_length=36, description="City ID"),
    db: Session = Depends(admin_auth),
) -> Dict[str, str]:
    return crud.delete_city(db, city_id)
