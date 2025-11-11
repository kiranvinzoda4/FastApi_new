import pytest

class TestHealthAPI:
    def test_basic_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_docs_endpoint(self, client):
        """Test API documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200