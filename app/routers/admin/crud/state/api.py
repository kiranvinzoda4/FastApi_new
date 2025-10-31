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


@router.get("/states", response_model=schemas.StateList, tags=["States"])
def get_states(
    start: int = 0,
    limit: int = 10,
    sort_by: Optional[str] = Query(None, max_length=50),
    order: Optional[str] = Query(None, max_length=4, description="asc | desc"),
    search: Optional[str] = Query(None, max_length=50),
    country_id: Optional[str] = Query(None, description="Filter by country ID"),
    db: Session = Depends(admin_auth),
):
    return crud.get_states(db, start, limit, sort_by, order, search, country_id)


@router.get(
    "/states/{state_id}", response_model=schemas.StateWithCountry, tags=["States"]
)
def get_state(state_id: str, db: Session = Depends(admin_auth)):
    return crud.get_state_by_id(db, state_id)


@router.post("/states", response_model=schemas.StateWithCountry, tags=["States"])
def create_state(state_data: schemas.StateCreate, db: Session = Depends(admin_auth)):
    return crud.create_state(db, state_data)


@router.put(
    "/states/{state_id}", response_model=schemas.StateWithCountry, tags=["States"]
)
def update_state(
    state_id: str, state_data: schemas.StateUpdate, db: Session = Depends(admin_auth)
):
    return crud.update_state(db, state_id, state_data)


@router.delete("/states/{state_id}", tags=["States"])
def delete_state(state_id: str, db: Session = Depends(admin_auth)):
    return crud.delete_state(db, state_id)
