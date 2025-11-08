import pytest
from fastapi.testclient import TestClient

class TestHealthAPI:
    def test_basic_health_check(self, client: TestClient):
        """Test basic health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_detailed_health_check(self, client: TestClient):
        """Test detailed health check endpoint"""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "timestamp" in data
        assert "uptime" in data
        
        # Check database status
        assert data["database"]["status"] in ["healthy", "unhealthy"]
    
    def test_health_check_response_format(self, client: TestClient):
        """Test health check response format"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        required_fields = ["status", "timestamp"]
        for field in required_fields:
            assert field in data