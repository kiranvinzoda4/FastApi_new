import pytest

@pytest.fixture
def sample_user_data():
    return {
        "first_name": "Test",
        "last_name": "User", 
        "email": "test@example.com",
        "password": "testpass123"
    }

@pytest.fixture
def sample_country_data():
    return {
        "name": "Test Country",
        "code": "TC"
    }

@pytest.fixture
def sample_state_data():
    return {
        "name": "Test State",
        "code": "TS",
        "country_id": "550e8400-e29b-41d4-a716-446655440000"
    }

@pytest.fixture
def sample_city_data():
    return {
        "name": "Test City",
        "state_id": "550e8400-e29b-41d4-a716-446655440000"
    }