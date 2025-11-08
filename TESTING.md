# Testing Guide

## Overview

This project uses pytest for comprehensive testing with unit and integration tests. Tests are isolated using SQLite and include coverage reporting.

## Quick Start

```bash
# Install dependencies
poetry install

# Run all tests
make test

# Run specific test types
make test-unit           # Unit tests only
make test-integration    # Integration tests only
make test-coverage       # With HTML coverage report
```

## Test Commands

### Using Make (Recommended)

| Command | Description |
|---------|-------------|
| `make test` | Run all tests with coverage |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make test-coverage` | Generate HTML coverage report |

### Using Poetry Directly

```bash
# All tests with coverage
poetry run pytest tests/ -v --cov=app --cov-report=term-missing

# Unit tests only
poetry run pytest tests/unit/ -v

# Integration tests only  
poetry run pytest tests/integration/ -v

# Specific test file
poetry run pytest tests/unit/test_security.py -v

# Specific test method
poetry run pytest tests/unit/test_security.py::TestSecurityUtils::test_hash_password -v

# Tests with specific markers
poetry run pytest -m "unit" -v
poetry run pytest -m "auth" -v
```

### Using Test Runner Script

```bash
# Different test types
python tests/test_runner.py --type unit
python tests/test_runner.py --type integration
python tests/test_runner.py --type all

# Options
python tests/test_runner.py --type unit --no-coverage --quiet --fail-fast
```

## Test Structure

```
tests/
├── fixtures/
│   └── test_data.py          # Test data factory for creating test objects
├── unit/                     # Unit tests (isolated, fast)
│   ├── test_security.py      # Security utilities (hashing, JWT, OTP)
│   ├── test_utils.py         # Utility functions (validation, datetime)
│   ├── test_email_templates.py # Email template rendering & XSS protection
│   └── test_models.py        # Database model creation & validation
├── integration/              # Integration tests (API endpoints)
│   ├── test_auth_api.py      # Authentication endpoints
│   └── test_health_api.py    # Health check endpoints
├── conftest.py               # Test configuration & fixtures
├── test_runner.py            # Custom test runner script
└── pytest.ini               # Pytest configuration
```

## Test Categories

### Unit Tests
- **Security**: Password hashing, JWT tokens, OTP generation
- **Utils**: ID generation, validation functions, datetime handling
- **Templates**: Email rendering, XSS protection
- **Models**: Database model creation and validation

### Integration Tests
- **Authentication API**: Login, profile, password reset
- **Health API**: Basic and detailed health checks
- **Database**: End-to-end database operations

## Fixtures & Test Data

### Available Fixtures

| Fixture | Description |
|---------|-------------|
| `db_session` | Isolated database session |
| `client` | FastAPI test client |
| `admin_user` | Test admin user |
| `customer_user` | Test customer |
| `vegetable` | Test vegetable product |
| `auth_headers` | Authentication headers for API calls |

### Test Data Factory

```python
from tests.fixtures.test_data import TestDataFactory

# Create test objects
admin = TestDataFactory.create_admin_user()
customer = TestDataFactory.create_customer(email="custom@test.com")
vegetable = TestDataFactory.create_vegetable(name="Custom Veg")
```

## Coverage Requirements

- **Minimum Coverage**: 80%
- **Coverage Reports**: 
  - Terminal: `--cov-report=term-missing`
  - HTML: `--cov-report=html` (saved to `htmlcov/`)
- **Coverage Config**: Defined in `pytest.ini`

## Test Configuration

### pytest.ini Settings
- Test discovery patterns
- Coverage requirements (80% minimum)
- Test markers for categorization
- Output formatting options

### Database Isolation
- **Test Database**: SQLite (fast, isolated)
- **Mocked Config**: Database settings mocked for tests
- **Automatic Cleanup**: Database reset between tests

## Writing Tests

### Unit Test Example

```python
import pytest
from app.security import SecurityUtils

class TestSecurity:
    def test_hash_password(self):
        password = "TestPassword123!"
        hashed = SecurityUtils.hash_password(password)
        
        assert hashed != password
        assert SecurityUtils.verify_password(password, hashed)
```

### Integration Test Example

```python
def test_admin_login(client, admin_user):
    response = client.post("/admin/admin-login", json={
        "email": admin_user.email,
        "password": "TestPass123!"
    })
    
    assert response.status_code == 200
    assert "token" in response.json()
```

## Test Markers

Use markers to categorize and run specific test groups:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration  
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_heavy_operation():
    pass
```

Run tests by marker:
```bash
poetry run pytest -m "unit" -v
poetry run pytest -m "integration" -v
```

## Continuous Integration

Tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    poetry install
    poetry run pytest tests/ --cov=app --cov-report=xml
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Tests use SQLite, not MySQL
2. **Import Errors**: Ensure `poetry install` is run first
3. **Coverage Failures**: Minimum 80% coverage required

### Debug Commands

```bash
# Run single test with detailed output
poetry run pytest tests/unit/test_security.py::TestSecurityUtils::test_hash_password -v -s

# Run tests without coverage for faster execution
poetry run pytest tests/unit/ -v --no-cov

# Run tests with pdb debugger
poetry run pytest tests/unit/test_security.py --pdb
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Fixtures**: Use fixtures for common test data
3. **Naming**: Clear, descriptive test names
4. **Coverage**: Aim for high coverage of critical paths
5. **Speed**: Keep unit tests fast, integration tests focused
6. **Mocking**: Mock external dependencies appropriately