import pytest

class TestBasicWorkflow:
    def test_app_startup_workflow(self, client):
        """Test basic app startup and health check workflow"""
        # Step 1: Check if app is running
        response = client.get("/health")
        assert response.status_code == 200
        
        # Step 2: Verify API docs are accessible
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Step 3: Verify OpenAPI spec is available
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data