from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.models import CityModel, StateModel
from .schemas import CityCreate, CityUpdate
from app.routers.admin.crud.crud import get_records, get_record, create_record, update_record, delete_record
from app.middleware.error_handler import handle_crud_errors


@handle_crud_errors
def get_cities(
    db: Session,
    start: int,
    limit: int,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    search: Optional[str] = None,
    state_id: Optional[str] = None,
    country_id: Optional[str] = None,
) -> Dict[str, Any]:
    # Input validation
    if start < 0:
        raise ValueError("Start must be non-negative")
    if limit <= 0 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")
    if order and order not in ["asc", "desc"]:
        raise ValueError("Order must be 'asc' or 'desc'")
    
    search_fields = ["name"] if search else None
    filters: Dict[str, Any] = {"is_deleted": False}
    
    if state_id:
        if len(state_id.strip()) == 0:
            raise ValueError("State ID cannot be empty")
        filters["state_id"] = state_id
    
    if country_id:
        if len(country_id.strip()) == 0:
            raise ValueError("Country ID cannot be empty")
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


@handle_crud_errors
def get_city_by_id(db: Session, city_id: str) -> CityModel:
    if not city_id or not city_id.strip():
        raise ValueError("City ID is required")
    
    return get_record(
        db=db,
        model_class=CityModel,
        filters={"id": city_id.strip(), "is_deleted": False}
    )


@handle_crud_errors
def create_city(db: Session, city: CityCreate) -> CityModel:
    # Validate state exists
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

    # Check for duplicate city name in same state
    existing_city = get_record(
        db=db,
        model_class=CityModel,
        filters={
            "name": city.name,
            "state_id": city.state_id,
            "is_deleted": False
        },
        exception=False
    )
    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="City with this name already exists in the state"
        )

    return create_record(db, CityModel, city)


@handle_crud_errors
def update_city(db: Session, city_id: str, city: CityUpdate) -> CityModel:
    if not city_id or not city_id.strip():
        raise ValueError("City ID is required")
    
    # Validate state exists
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

    # Check for duplicate city name in same state (excluding current city)
    existing_city = get_record(
        db=db,
        model_class=CityModel,
        filters={
            "name": city.name,
            "state_id": city.state_id,
            "is_deleted": False
        },
        exception=False
    )
    if existing_city and existing_city.id != city_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="City with this name already exists in the state"
        )

    return update_record(db, CityModel, city_id.strip(), city)


@handle_crud_errors
def delete_city(db: Session, city_id: str) -> Dict[str, str]:
    if not city_id or not city_id.strip():
        raise ValueError("City ID is required")
    
    result = delete_record(db, CityModel, city_id.strip())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    return {"detail": "City deleted successfully"}