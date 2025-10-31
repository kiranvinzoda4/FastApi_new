from fastapi import APIRouter, Query, Depends, Header, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.security import get_current_user
from . import crud, schemas

router = APIRouter()


def admin_auth(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Token validation dependency."""
    return db


@router.get("/cities", response_model=schemas.CityList, tags=["Cities"])
def get_cities(
    start: int = 0,
    limit: int = 10,
    sort_by: Optional[str] = Query(None, max_length=50),
    order: Optional[str] = Query(None, max_length=4, description="asc | desc"),
    search: Optional[str] = Query(None, max_length=50),
    state_id: Optional[str] = Query(None, description="Filter by state ID"),
    country_id: Optional[str] = Query(None, description="Filter by country ID"),
    db: Session = Depends(admin_auth),
):
    return crud.get_cities(
        db, start, limit, sort_by, order, search, state_id, country_id
    )


@router.get("/cities/{city_id}", response_model=schemas.CityWithState, tags=["Cities"])
def get_city(city_id: str, db: Session = Depends(admin_auth)):
    return crud.get_city_by_id(db, city_id)


@router.post("/cities", response_model=schemas.CityWithState, tags=["Cities"])
def create_city(city_data: schemas.CityCreate, db: Session = Depends(admin_auth)):
    return crud.create_city(db, city_data)


@router.put("/cities/{city_id}", response_model=schemas.CityWithState, tags=["Cities"])
def update_city(
    city_id: str, city_data: schemas.CityUpdate, db: Session = Depends(admin_auth)
):
    return crud.update_city(db, city_id, city_data)


@router.delete("/cities/{city_id}", tags=["Cities"])
def delete_city(city_id: str, db: Session = Depends(admin_auth)):
    return crud.delete_city(db, city_id)
