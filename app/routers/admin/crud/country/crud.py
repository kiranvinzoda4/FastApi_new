from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.models import CountryModel
from .schemas import CountryCreate, CountryUpdate
from app.routers.admin.crud.crud import (
    get_records,
    get_record,
    create_record,
    update_record,
    delete_record,
)



def get_countries(
    db: Session,
    start: int,
    limit: int,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    search: Optional[str] = None,
) -> Dict[str, Any]:
    search_fields = ["name", "code"] if search else None
    filters: Dict[str, Any] = {"is_deleted": False}
    
    return get_records(
        db=db,
        model_class=CountryModel,
        start=start,
        limit=limit,
        search=search,
        search_fields=search_fields,
        sort_by=sort_by,
        order=order,
        filters=filters,
    )


def get_country_by_id(db: Session, country_id: str) -> CountryModel:
    return get_record(
        db=db,
        model_class=CountryModel,
        filters={"id": country_id.strip(), "is_deleted": False},
    )


def create_country(db: Session, country: CountryCreate) -> CountryModel:
    # Check for duplicate country code
    existing_code = get_record(
        db=db,
        model_class=CountryModel,
        filters={"code": country.code.upper(), "is_deleted": False},
        exception=False,
    )
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Country code already exists"
        )
    # Check for duplicate country name
    existing_name = get_record(
        db=db,
        model_class=CountryModel,
        filters={"name": country.name, "is_deleted": False},
        exception=False,
    )
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Country name already exists"
        )
    # Normalize country code to uppercase
    country.code = country.code.upper()
    return create_record(db, CountryModel, country)


def update_country(
    db: Session, country_id: str, country: CountryUpdate
) -> CountryModel:
    # Check for duplicate country code (excluding current country)
    existing_code = get_record(
        db=db,
        model_class=CountryModel,
        filters={"code": country.code.upper(), "is_deleted": False},
        exception=False,
    )
    if existing_code and existing_code.id != country_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Country code already exists"
        )
    # Check for duplicate country name (excluding current country)
    existing_name = get_record(
        db=db,
        model_class=CountryModel,
        filters={"name": country.name, "is_deleted": False},
        exception=False,
    )
    if existing_name and existing_name.id != country_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Country name already exists"
        )
    # Normalize country code to uppercase
    country.code = country.code.upper()
    return update_record(db, CountryModel, country_id.strip(), country)


def delete_country(db: Session, country_id: str) -> Dict[str, str]:
    # Check if country has states before deletion
    from app.models import StateModel

    states = get_record(
        db=db,
        model_class=StateModel,
        filters={"country_id": country_id.strip(), "is_deleted": False},
        exception=False,
    )
    if states:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete country with existing states",
        )
    result = delete_record(db, CountryModel, country_id.strip())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
        )
    return {"detail": "Country deleted successfully"}