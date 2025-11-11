from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user
from . import crud, schemas

router = APIRouter()

def admin_auth(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)) -> Session:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return db

@router.get("/states", response_model=schemas.StateList, tags=["States"], summary="Get all states", description="GET /states - Retrieve paginated list of states with optional filtering by country")
async def get_states(
    start: int = Query(0, ge=0, description="Starting offset"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    sort_by: Optional[str] = Query(None, max_length=50),
    order: Optional[str] = Query(None, regex="^(asc|desc)$", description="asc | desc"),
    search: Optional[str] = Query(None, max_length=50),
    country_id: Optional[str] = Query(None, description="Filter by country ID"),
    db: Session = Depends(admin_auth),
) -> schemas.StateList:
    return crud.get_states(db, start, limit, sort_by, order, search, country_id)

@router.get(
    "/states/{state_id}", response_model=schemas.StateWithCountry, tags=["States"], summary="Get state by ID", description="GET /states/{id} - Retrieve a specific state by its ID"
)
async def get_state(
    state_id: str = Path(..., min_length=36, max_length=36, description="State ID"),
    db: Session = Depends(admin_auth)
) -> schemas.StateWithCountry:
    return crud.get_state_by_id(db, state_id)

@router.post("/states", response_model=schemas.StateWithCountry, tags=["States"], summary="Create new state", description="POST /states - Create a new state")
async def create_state(
    state_data: schemas.StateCreate,
    db: Session = Depends(admin_auth)
) -> schemas.StateWithCountry:
    return crud.create_state(db, state_data)

@router.put(
    "/states/{state_id}", response_model=schemas.StateWithCountry, tags=["States"], summary="Update state", description="PUT /states/{id} - Update an existing state"
)
async def update_state(
    state_id: str = Path(..., min_length=36, max_length=36, description="State ID"),
    state_data: schemas.StateUpdate = ...,
    db: Session = Depends(admin_auth)
) -> schemas.StateWithCountry:
    return crud.update_state(db, state_id, state_data)

@router.delete("/states/{state_id}", tags=["States"], summary="Delete state", description="DELETE /states/{id} - Soft delete a state")
async def delete_state(
    state_id: str = Path(..., min_length=36, max_length=36, description="State ID"),
    db: Session = Depends(admin_auth)
) -> Dict[str, str]:
    return crud.delete_state(db, state_id)