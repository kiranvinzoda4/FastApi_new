import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Import fixtures
from tests.fixtures.test_data import *

SQLITE_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_settings():
    with patch('app.config.settings') as mock:
        mock.ACCESS_JWT_KEY = '{"k":"dGVzdGtleWZvcmp3dHRlc3RpbmdwdXJwb3Nlc29ubHk","kty":"oct"}'
        mock.REFRESH_JWT_KEY = '{"k":"dGVzdGtleWZvcmp3dHRlc3RpbmdwdXJwb3Nlc29ubHk","kty":"oct"}'
        mock.SMTP_USER = "test@example.com"
        mock.SMTP_PASSWORD = "testpass"
        yield mock

def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "e2e: End-to-end tests")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location"""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

def pytest_sessionstart(session):
    """Print clean startup message"""
    print("\nFastAPI Test Suite")
    print("=" * 20)

def pytest_sessionfinish(session, exitstatus):
    """Print clean completion message"""
    if exitstatus == 0:
        print("\nAll tests passed!")
    else:
        print(f"\n{exitstatus} test(s) failed")

def pytest_runtest_logstart(nodeid, location):
    """Custom test start logging"""
    pass  # Keep quiet during individual test runs

def pytest_runtest_logfinish(nodeid, location):
    """Custom test finish logging"""
    pass  # Keep quiet during individual test runs