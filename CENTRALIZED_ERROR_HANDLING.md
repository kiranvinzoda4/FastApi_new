# Centralized Error Handling

This project now uses a single, centralized error handling system that eliminates the need for scattered try-catch blocks and logging statements throughout the codebase.

## How It Works

### 1. Single Error Handler
All errors are handled by `app.core.error_handler.ErrorHandler` which:
- Converts exceptions to appropriate HTTP responses
- Logs errors at the correct level (warning/error)
- Provides consistent error messages

### 2. Simple Decorator
Use `@handle_errors` decorator on any function:

```python
from app.core.error_handler import handle_errors

@handle_errors
def my_function():
    # Your code here - no try/catch needed
    # Just raise exceptions and they'll be handled automatically
    if something_wrong:
        raise ValueError("Something is wrong")
    return result
```

### 3. Centralized Logging
Single logging configuration in `app.core.logger.py`:
- Console output for INFO and above
- File logging for DEBUG and above
- Automatic log rotation

## Migration Complete

The following old files have been removed:
- `app/middleware/error_handler.py`
- `app/middleware/error_logging.py` 
- `app/exceptions.py`
- `app/logging_config.py`

All functionality is now handled by:
- `app/core/error_handler.py` - Error handling
- `app/core/logger.py` - Logging configuration

## Usage Examples

### API Endpoints
```python
@router.post("/")
@handle_errors
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    # No try/catch needed - just business logic
    if not item.name:
        raise ValueError("Name is required")
    return crud.create_item(db, item)
```

### Service Functions
```python
@handle_errors
def send_notification(user_id: str):
    # No try/catch needed
    if not user_id:
        raise ValueError("User ID required")
    # Send notification logic
    return True
```

### Database Operations
```python
@handle_errors
def get_user(db: Session, user_id: str):
    # No try/catch needed
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

## Benefits

1. **Less Code**: No more repetitive try/catch blocks
2. **Consistent**: All errors handled the same way
3. **Maintainable**: Single place to modify error handling
4. **Clean**: Focus on business logic, not error handling
5. **Automatic**: Logging happens automatically at the right level