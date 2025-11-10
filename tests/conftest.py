import pytest
import tempfile
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Mock database configuration for tests
@pytest.fixture(scope="session", autouse=True)
def mock_database_config():
    """Mock database configuration to avoid MySQL connection during tests"""
    with patch('app.config.settings') as mock_settings:
        mock_settings.DB_HOST = "localhost"
        mock_settings.DB_PORT = 3306
        mock_settings.DB_USER = "test"
        mock_settings.DB_PASSWORD = "test"
        mock_settings.DB_NAME = "test_db"
        mock_settings.DB_POOL_SIZE = 5
        mock_settings.WEB_CONCURRENCY = 1
        mock_settings.DEBUG = False
        mock_settings.ACCESS_JWT_KEY = {"k": "test_key", "kty": "oct"}
        mock_settings.REFRESH_JWT_KEY = {"k": "test_refresh_key", "kty": "oct"}
        yield mock_settings
@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    db_fd, db_path = tempfile.mkstemp()
    test_database_url = f"sqlite:///{db_path}"
    engine = create_engine(
        test_database_url, 
        connect_args={"check_same_thread": False}
    )
    # Import Base after mocking config
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    os.close(db_fd)
    os.unlink(db_path)
@pytest.fixture
def db_session(test_db):
    """Create database session for tests"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
@pytest.fixture
def client(db_session, mock_database_config):
    """Create test client with database override"""
    # Import after mocking
    from app.main import app
    from app.database import get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
@pytest.fixture
def admin_user(db_session):
    """Create test admin user"""
    from tests.fixtures.test_data import TestDataFactory
    user = TestDataFactory.create_admin_user()
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
@pytest.fixture
def customer_user(db_session):
    """Create test customer"""
    from tests.fixtures.test_data import TestDataFactory
    customer = TestDataFactory.create_customer()
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer
@pytest.fixture
def vegetable(db_session):
    """Create test vegetable"""
    from tests.fixtures.test_data import TestDataFactory
    veg = TestDataFactory.create_vegetable()
    db_session.add(veg)
    db_session.commit()
    db_session.refresh(veg)
    return veg
@pytest.fixture
def auth_headers(admin_user, mock_database_config):
    """Create authentication headers for admin user"""
    from app.security import SecurityUtils
    token = SecurityUtils.create_access_token({"sub": admin_user.id, "email": admin_user.email})
    return {"Authorization": f"Bearer {token}"}
