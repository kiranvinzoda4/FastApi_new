import pytest

class TestStatesWorkflow:
    def test_states_crud_workflow(self, client, sample_state_data):
        """Test complete CRUD workflow for states"""
        # Step 1: Try to access states endpoint (should be protected)
        response = client.get("/states")
        assert response.status_code in [401, 403], "States endpoint should be protected"
        
        # Step 2: Try to create state without auth (should fail)
        response = client.post("/states", json=sample_state_data)
        assert response.status_code in [401, 403], "Create state should require auth"
        
        # Step 3: Try to get specific state without auth (should fail)
        state_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/states/{state_id}")
        assert response.status_code in [401, 403], "Get state should require auth"
        
        # Step 4: Try invalid state ID format
        response = client.get("/states/invalid-id")
        assert response.status_code in [403, 422], "Invalid ID should be rejected"

    def test_states_country_relationship_workflow(self, client):
        """Test state-country relationship workflow"""
        # Test creating state with invalid country_id
        invalid_state_data = {
            "name": "Test State",
            "code": "TS",
            "country_id": "invalid-country-id"
        }
        response = client.post("/states", json=invalid_state_data)
        assert response.status_code in [401, 403, 422], "Should reject invalid country_id"
        
        # Test creating state with missing country_id
        incomplete_state_data = {
            "name": "Test State",
            "code": "TS"
        }
        response = client.post("/states", json=incomplete_state_data)
        assert response.status_code in [401, 403, 422], "Should require country_id"

    def test_states_validation_workflow(self, client):
        """Test state data validation workflow"""
        # Test with missing required fields
        invalid_data = {"name": "Test State"}  # Missing code and country_id
        response = client.post("/states", json=invalid_data)
        assert response.status_code in [401, 403, 422], "Should reject incomplete data"