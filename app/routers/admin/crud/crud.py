import logging
from typing import Any, Dict, List, Optional, Type, Union, Tuple

from fastapi import HTTPException, status
from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session, aliased, class_mapper, Query
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.sqltypes import String as SQLAlchemyString
from sqlalchemy.inspection import inspect
from app.libs.utils import generate_id, now

logger = logging.getLogger(__name__)


def get_record_by_id(
    db: Session,
    model_class: Type[DeclarativeMeta],
    id: str
) -> Optional[Any]:
    return (
        db.query(model_class)
        .filter(
            model_class.id == id,
            model_class.is_deleted.is_(False),
        )
        .first()
    )
    
    
        
def get_record_by_value(
    db: Session,
    model_class: Type[DeclarativeMeta],
    value: str
) -> Optional[Any]:
    try:
        return (
            db.query(model_class)
            .filter(
                model_class.value == value,
                model_class.is_deleted.is_(False),
            )
            .first()
        )
    except Exception as e:
        logger.error(f"Database error in get_record_by_value: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    

def validate_filter_keys(model_class: DeclarativeMeta, filters: Dict[str, Any]) -> None:
    valid_columns = set(c.name for c in model_class.__table__.columns)
    
    for key in filters:
        if key not in valid_columns:
            raise ValueError(f"Invalid column '{key}' for model '{model_class.__name__}'")

def apply_filters(query: Query, model_class: Type[DeclarativeMeta], filters: Dict[str, Any]) -> Query:
    aliases: Dict[str, Any] = {}

    for full_field, value in filters.items():
        path_parts = full_field.split('.')
        current_model = model_class
        current_path = []
        current_alias = None

        for part in path_parts[:-1]:
            current_path.append(part)
            path_str = ".".join(current_path)

            # If already aliased, use it
            if path_str in aliases:
                current_alias = aliases[path_str]
            else:
                attr = getattr(current_model, part, None)

                if not isinstance(attr, InstrumentedAttribute):
                    raise HTTPException(status_code=400, detail=f"Invalid relationship: {part}")

                relationship = class_mapper(current_model).relationships.get(part)
                if not relationship:
                    raise HTTPException(status_code=400, detail=f"Invalid relationship: {part}")

                related_model = relationship.mapper.class_
                current_alias = aliased(related_model)

                if len(current_path) == 1:
                    query = query.join(current_alias, attr)
                else:
                    parent_path = ".".join(current_path[:-1])
                    parent_alias = aliases[parent_path]
                    query = query.join(current_alias, getattr(parent_alias, part))

                aliases[path_str] = current_alias
                current_model = related_model

        column_name = path_parts[-1]
        target_model = current_alias if current_alias else model_class
        column = getattr(target_model, column_name, None)

        if column is None:
            raise HTTPException(status_code=400, detail=f"Invalid field: {full_field}")

        if isinstance(value, list):
            query = query.filter(column.in_(value))
        else:
            query = query.filter(column == value)


    return query


def apply_search_sort(
    query: Query, 
    model_class: Type[DeclarativeMeta], 
    path: str, 
    aliases: Dict[str, Any], 
    is_search: bool = True
) -> Tuple[Query, Any]:
    current_model = model_class
    current_path: List[str] = []
    current_alias = None
    # target_model = model_class
    
    for part in path.split(".")[:-1]:
        current_path.append(part)
        path_str = ".".join(current_path)
        if path_str in aliases:
            current_alias = aliases[path_str]
        else:
            attr = getattr(current_model, part, None)

            if not isinstance(attr, InstrumentedAttribute):
                raise HTTPException(status_code=400, detail=f"Invalid relationship: {part}")

            relationship = class_mapper(current_model).relationships.get(part)
            if not relationship:
                raise HTTPException(status_code=400, detail=f"Invalid relationship: {part}")

            related_model = relationship.mapper.class_
            current_alias = aliased(related_model)

            if len(current_path) == 1:
                query = query.outerjoin(current_alias, attr)
                # query = query.join(current_alias, attr) if is_search else query.outerjoin(current_alias, attr)
            else:
                parent_path = ".".join(current_path[:-1])
                parent_alias = aliases[parent_path]
                query = query.outerjoin(current_alias, getattr(parent_alias, part))
                # query = query.join(current_alias, getattr(parent_alias, part)) if is_search else query.outerjoin(current_alias, getattr(parent_alias, part))

            aliases[path_str] = current_alias
            current_model = related_model

    target_model = current_alias if current_alias else model_class
    column_name = path.split(".")[-1]
    column = getattr(target_model, column_name, None)
    if column is None:
        raise HTTPException(status_code=400, detail=f"Invalid field: {path.split('.')[-1]}")
    
    if len(path.split(".")) <= 1:
        column = getattr(current_model, path, None)
        if column is None:
            raise HTTPException(status_code=400, detail=f"Invalid field: {path}")
        
    return query, column


def get_sort_field(sort_by: str, sort_listing: List[str]) -> str:
    if sort_by in sort_listing:
        return sort_by
    for field in sort_listing:
        if sort_by in field.split(".")[:-1]:
            return field
    raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")


def get_records(
    db: Session,
    model_class: Type[DeclarativeMeta],
    start: int,
    limit: int,
    search: Optional[str] = None,
    search_fields: Optional[List[str]] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    custom_filter_conditions: Optional[Any] = None,
    execution_opts: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    query = db.query(model_class)
    if execution_opts:
        query = query.execution_options(**execution_opts)
    if filters:
        query = apply_filters(query, model_class, filters)
    if custom_filter_conditions is not None:
        query = query.filter(custom_filter_conditions)

    if search and search_fields:
        search_pattern = f"%{search.strip()}%"
        search_conditions = []
        aliases: Dict[str, Any] = {}

        for field in search_fields:
            query, column = apply_search_sort(query, model_class, field, aliases)
            try:
                if not isinstance(column.type, SQLAlchemyString):
                    column = cast(column, String)
            except AttributeError:
                column = cast(column, String)

            search_conditions.append(column.ilike(search_pattern))
        query = query.filter(or_(*search_conditions))

    
    if sort_by:
        sort_aliases: Dict[str, Any] = {}
        query, sort_field = apply_search_sort(query, model_class, sort_by, sort_aliases, is_search=False)
        query = query.order_by(sort_field.desc() if order == "desc" else sort_field)
    else:
        query = query.order_by(model_class.created_at.desc())

    results = query.offset(start).limit(limit).all()

    count = query.count()

    return {"count": count, "list": results}


def get_record(
    db: Session,
    model_class: Type[DeclarativeMeta],
    filters: Dict[str, Any],
    exception: bool = True,
    execution_opts: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    
    validate_filter_keys(model_class, filters)
    
    query = db.query(model_class)
    if execution_opts:
        query = query.execution_options(**execution_opts)
    for key, value in filters.items():
        column = getattr(model_class, key)
        if isinstance(value, str):
            query = query.filter(func.lower(column) == value.lower())
        else:
            query = query.filter(column == value)

    db_record = query.first()

    if exception and not db_record:
        model_name = model_class.__name__.replace("Model", "")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model_name} not found",
        )

    return db_record

def create_record(db: Session, model_class: Type[DeclarativeMeta], request_schema: Any) -> Any:

    record = model_class(id=generate_id(), **request_schema.model_dump())
    db.add(record)
    db.commit()
    return record


def update_record(db: Session, model_class: Type[DeclarativeMeta], record_id: str, request_schema: Any) -> Any:

    db_record = (
        db.query(model_class)
        .filter(model_class.id == record_id, model_class.is_deleted.is_(False))
        .first()
    )

    if not db_record:
        model_name = model_class.__name__.replace("Model", "")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model_name} not found",
        )

    for field, value in request_schema.model_dump().items():
        setattr(db_record, field, value)

    db_record.updated_at = now()
    db.commit()
    return db_record


def delete_record(db: Session, model_class: Type[DeclarativeMeta], record_id: str) -> Any:

    db_record = (
        db.query(model_class)
        .filter(model_class.id == record_id, model_class.is_deleted.is_(False))
        .first()
    )

    if not db_record:
        model_name = model_class.__name__.replace("Model", "")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model_name} not found",
        )

    db_record.is_deleted = True
    db_record.updated_at = now()
    db.commit()
    return db_record


def has_any_child_relation(
    db: Session,
    parent_model: Type[DeclarativeMeta],
    parent_id: str,
    soft_delete_field: str = "is_deleted",
    exclude_relationships: Optional[List[str]] = None
) -> bool:
    
    parent = db.get(parent_model, parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    relationships = inspect(parent_model).relationships
    for rel_name, rel in relationships.items():
        if exclude_relationships and rel_name in exclude_relationships:
            continue
        if rel.direction.name not in ("ONETOMANY", "MANYTOMANY"):
            continue

        related_objs = getattr(parent, rel_name, [])
        if related_objs is None:
            continue
        
        for obj in related_objs:
            if not getattr(obj, soft_delete_field, False):
                return True

    return False


def find_child_data(
    db: Session,
    target_model: Type[DeclarativeMeta],
    target_id: str,
    include_tables: Optional[List[str]] = None,
    exclude_tables: Optional[List[str]] = None
) -> bool:
    target_column = target_model.__table__.c.id
    metadata = target_model.__table__.metadata

    referenced_in: List[Dict[str, str]] = []

    for table in metadata.tables.values():
        if include_tables and table.name not in include_tables:
            continue
        if exclude_tables and table.name in exclude_tables:
            continue

        for column in table.columns:
            for fk in column.foreign_keys:
                if fk.column == target_column:
                    exists = db.query(table).filter(column == target_id).first()
                    if exists:
                        referenced_in.append({
                            "from_table": table.name,
                            "column": column.name,
                            "references": str(fk.column)
                        })

    return bool(referenced_in)