from fastapi import APIRouter, Query, Depends, Header, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.routers.admin.crud import admin_users
from . import crud, schemas

router = APIRouter()


def admin_auth(token: str = Header(None), db: Session = Depends(get_db)):
    """Token validation dependency."""
    admin_users.verify_token(db, token=token)
    return db


@router.get("/countries", response_model=schemas.CountryList, tags=["Countries"])
def get_countries(
    start: int = 0,
    limit: int = 10,
    sort_by: Optional[str] = Query(None, max_length=50),
    order: Optional[str] = Query(None, max_length=4, description="asc | desc"),
    search: Optional[str] = Query(None, max_length=50),
    db: Session = Depends(admin_auth),
):
    return crud.get_countries(db, start, limit, sort_by, order, search)


@router.get(
    "/countries/{country_id}", response_model=schemas.Country, tags=["Countries"]
)
def get_country(country_id: str, db: Session = Depends(admin_auth)):
    return crud.get_country_by_id(db, country_id)


@router.post("/countries", response_model=schemas.Country, tags=["Countries"])
def create_country(
    country_data: schemas.CountryCreate, db: Session = Depends(admin_auth)
):
    return crud.create_country(db, country_data)


@router.put(
    "/countries/{country_id}", response_model=schemas.Country, tags=["Countries"]
)
def update_country(
    country_id: str,
    country_data: schemas.CountryUpdate,
    db: Session = Depends(admin_auth),
):
    return crud.update_country(db, country_id, country_data)


@router.delete("/countries/{country_id}", tags=["Countries"])
def delete_country(country_id: str, db: Session = Depends(admin_auth)):
    return crud.delete_country(db, country_id)
