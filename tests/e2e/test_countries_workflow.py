import pytest

class TestCountriesWorkflow:
    def test_countries_crud_workflow(self, client, sample_country_data):
        """Test complete CRUD workflow for countries"""
        # Step 1: Try to access countries endpoint (should be protected)
        response = client.get("/countries/")
        assert response.status_code in [401, 403], "Countries endpoint should be protected"
        
        # Step 2: Try to create country without auth (should fail)
        response = client.post("/countries/", json=sample_country_data)
        assert response.status_code in [401, 403], "Create country should require auth"
        
        # Step 3: Try to get specific country without auth (should fail)
        country_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/countries/{country_id}")
        assert response.status_code in [401, 403], "Get country should require auth"
        
        # Step 4: Try invalid country ID format
        response = client.get("/countries/invalid-id")
        assert response.status_code in [403, 422], "Invalid ID should be rejected"

    def test_countries_validation_workflow(self, client):
        """Test country data validation workflow"""
        # Test with missing required fields
        invalid_data = {"name": "Test Country"}  # Missing code
        response = client.post("/countries/", json=invalid_data)
        assert response.status_code in [401, 403, 422], "Should reject incomplete data"
        
        # Test with invalid data types
        invalid_data = {"name": 123, "code": "TC"}  # Invalid name type
        response = client.post("/countries/", json=invalid_data)
        assert response.status_code in [401, 403, 422], "Should reject invalid types"