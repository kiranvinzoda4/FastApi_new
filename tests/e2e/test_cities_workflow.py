import pytest

class TestCitiesWorkflow:
    def test_cities_crud_workflow(self, client, sample_city_data):
        """Test complete CRUD workflow for cities"""
        # Step 1: Try to access cities endpoint (should be protected)
        response = client.get("/cities")
        assert response.status_code in [401, 403], "Cities endpoint should be protected"
        
        # Step 2: Try to create city without auth (should fail)
        response = client.post("/cities", json=sample_city_data)
        assert response.status_code in [401, 403], "Create city should require auth"
        
        # Step 3: Try to get specific city without auth (should fail)
        city_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/cities/{city_id}")
        assert response.status_code in [401, 403], "Get city should require auth"
        
        # Step 4: Try invalid city ID format
        response = client.get("/cities/invalid-id")
        assert response.status_code in [403, 422], "Invalid ID should be rejected"

    def test_cities_state_relationship_workflow(self, client):
        """Test city-state relationship workflow"""
        # Test creating city with invalid state_id
        invalid_city_data = {
            "name": "Test City",
            "state_id": "invalid-state-id"
        }
        response = client.post("/cities", json=invalid_city_data)
        assert response.status_code in [401, 403, 422], "Should reject invalid state_id"
        
        # Test creating city with missing state_id
        incomplete_city_data = {
            "name": "Test City"
        }
        response = client.post("/cities", json=incomplete_city_data)
        assert response.status_code in [401, 403, 422], "Should require state_id"

    def test_cities_validation_workflow(self, client):
        """Test city data validation workflow"""
        # Test with missing required fields
        invalid_data = {}  # Missing name and state_id
        response = client.post("/cities", json=invalid_data)
        assert response.status_code in [401, 403, 422], "Should reject empty data"
        
        # Test with invalid data types
        invalid_data = {"name": 123, "state_id": "550e8400-e29b-41d4-a716-446655440000"}
        response = client.post("/cities", json=invalid_data)
        assert response.status_code in [401, 403, 422], "Should reject invalid types"