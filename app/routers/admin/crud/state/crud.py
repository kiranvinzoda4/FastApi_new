from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.models import StateModel, CountryModel
from .schemas import StateCreate, StateUpdate
from app.routers.admin.crud.crud import get_records, get_record, create_record, update_record, delete_record
from app.middleware.error_handler import handle_crud_errors


@handle_crud_errors
def get_states(
    db: Session,
    start: int,
    limit: int,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    search: Optional[str] = None,
    country_id: Optional[str] = None,
) -> Dict[str, Any]:
    # Input validation
    if start < 0:
        raise ValueError("Start must be non-negative")
    if limit <= 0 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")
    if order and order not in ["asc", "desc"]:
        raise ValueError("Order must be 'asc' or 'desc'")
    
    search_fields = ["name", "code"] if search else None
    filters: Dict[str, Any] = {"is_deleted": False}
    
    if country_id:
        if len(country_id.strip()) == 0:
            raise ValueError("Country ID cannot be empty")
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


@handle_crud_errors
def get_state_by_id(db: Session, state_id: str) -> StateModel:
    if not state_id or not state_id.strip():
        raise ValueError("State ID is required")
    
    return get_record(
        db=db,
        model_class=StateModel,
        filters={"id": state_id.strip(), "is_deleted": False}
    )


@handle_crud_errors
def create_state(db: Session, state: StateCreate) -> StateModel:
    # Validate country exists
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

    # Check for duplicate state name in same country
    existing_state = get_record(
        db=db,
        model_class=StateModel,
        filters={
            "name": state.name,
            "country_id": state.country_id,
            "is_deleted": False
        },
        exception=False
    )
    if existing_state:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="State with this name already exists in the country"
        )

    return create_record(db, StateModel, state)


@handle_crud_errors
def update_state(db: Session, state_id: str, state: StateUpdate) -> StateModel:
    if not state_id or not state_id.strip():
        raise ValueError("State ID is required")
    
    # Validate country exists
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

    # Check for duplicate state name in same country (excluding current state)
    existing_state = get_record(
        db=db,
        model_class=StateModel,
        filters={
            "name": state.name,
            "country_id": state.country_id,
            "is_deleted": False
        },
        exception=False
    )
    if existing_state and existing_state.id != state_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="State with this name already exists in the country"
        )

    return update_record(db, StateModel, state_id.strip(), state)


@handle_crud_errors
def delete_state(db: Session, state_id: str) -> Dict[str, str]:
    if not state_id or not state_id.strip():
        raise ValueError("State ID is required")
    
    # Check if state has cities before deletion
    from app.models import CityModel
    cities = get_record(
        db=db,
        model_class=CityModel,
        filters={"state_id": state_id.strip(), "is_deleted": False},
        exception=False
    )
    if cities:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete state with existing cities"
        )
    
    result = delete_record(db, StateModel, state_id.strip())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )
    
    return {"detail": "State deleted successfully"}