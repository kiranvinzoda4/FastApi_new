from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import StateModel, CountryModel
from .schemas import StateCreate, StateUpdate
from app.routers.admin.crud.crud import get_records, get_record, create_record, update_record, delete_record
from typing import Optional


def get_states(
    db: Session,
    start: int,
    limit: int,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    search: Optional[str] = None,
    country_id: Optional[str] = None,
):
    search_fields = ["name", "code"] if search else None
    filters = {"is_deleted": False}
    if country_id:
        filters["country_id"] = country_id
    
    return get_records(
        db=db,
        model_class=StateModel,
        start=start,
        limit=limit,
        search=search,
        search_fields=search_fields,
        sort_by=sort_by,
        order=order,
        filters=filters
    )


def get_state_by_id(db: Session, state_id: str):
    return get_record(
        db=db,
        model_class=StateModel,
        filters={"id": state_id, "is_deleted": False}
    )


def create_state(db: Session, state: StateCreate):
    country = get_record(
        db=db,
        model_class=CountryModel,
        filters={"id": state.country_id, "is_deleted": False},
        exception=False
    )
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )

    return create_record(db, StateModel, state)


def update_state(db: Session, state_id: str, state: StateUpdate):
    country = get_record(
        db=db,
        model_class=CountryModel,
        filters={"id": state.country_id, "is_deleted": False},
        exception=False
    )
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )

    return update_record(db, StateModel, state_id, state)


def delete_state(db: Session, state_id: str):
    delete_record(db, StateModel, state_id)
    return {"detail": "State deleted successfully"}