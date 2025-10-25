import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test basic health check endpoint"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_ping(client: TestClient):
    """Test ping endpoint"""
    response = client.get("/health/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data