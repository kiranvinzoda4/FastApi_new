from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import CountryModel
from .schemas import CountryCreate, CountryUpdate
from app.routers.admin.crud.crud import get_records, get_record, create_record, update_record, delete_record
from typing import Optional


def get_countries(
    db: Session,
    start: int,
    limit: int,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    search: Optional[str] = None,
):
    search_fields = ["name", "code"] if search else None
    filters = {"is_deleted": False}
    
    return get_records(
        db=db,
        model_class=CountryModel,
        start=start,
        limit=limit,
        search=search,
        search_fields=search_fields,
        sort_by=sort_by,
        order=order,
        filters=filters
    )


def get_country_by_id(db: Session, country_id: str):
    return get_record(
        db=db,
        model_class=CountryModel,
        filters={"id": country_id, "is_deleted": False}
    )


def create_country(db: Session, country: CountryCreate):
    existing = get_record(
        db=db,
        model_class=CountryModel,
        filters={"code": country.code, "is_deleted": False},
        exception=False
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country code already exists"
        )

    return create_record(db, CountryModel, country)


def update_country(db: Session, country_id: str, country: CountryUpdate):
    existing = get_record(
        db=db,
        model_class=CountryModel,
        filters={"code": country.code, "is_deleted": False},
        exception=False
    )
    if existing and existing.id != country_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country code already exists"
        )

    return update_record(db, CountryModel, country_id, country)


def delete_country(db: Session, country_id: str):
    delete_record(db, CountryModel, country_id)
    return {"detail": "Country deleted successfully"}