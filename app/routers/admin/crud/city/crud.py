from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import CityModel, StateModel
from .schemas import CityCreate, CityUpdate
from app.routers.admin.crud.crud import get_records, get_record, create_record, update_record, delete_record
from typing import Optional


def get_cities(
    db: Session,
    start: int,
    limit: int,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    search: Optional[str] = None,
    state_id: Optional[str] = None,
    country_id: Optional[str] = None,
):
    search_fields = ["name"] if search else None
    filters = {"is_deleted": False}
    if state_id:
        filters["state_id"] = state_id
    if country_id:
        filters["state.country_id"] = country_id
    
    return get_records(
        db=db,
        model_class=CityModel,
        start=start,
        limit=limit,
        search=search,
        search_fields=search_fields,
        sort_by=sort_by,
        order=order,
        filters=filters
    )


def get_city_by_id(db: Session, city_id: str):
    return get_record(
        db=db,
        model_class=CityModel,
        filters={"id": city_id, "is_deleted": False}
    )


def create_city(db: Session, city: CityCreate):
    state = get_record(
        db=db,
        model_class=StateModel,
        filters={"id": city.state_id, "is_deleted": False},
        exception=False
    )
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    return create_record(db, CityModel, city)


def update_city(db: Session, city_id: str, city: CityUpdate):
    state = get_record(
        db=db,
        model_class=StateModel,
        filters={"id": city.state_id, "is_deleted": False},
        exception=False
    )
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    return update_record(db, CityModel, city_id, city)


def delete_city(db: Session, city_id: str):
    delete_record(db, CityModel, city_id)
    return {"detail": "City deleted successfully"}