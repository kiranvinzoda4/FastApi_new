import pytest

class TestStatesAPI:
    def test_get_states_endpoint_exists(self, client):
        """Test states endpoint exists (may be protected)"""
        response = client.get("/states")
        # Should return 403 (forbidden) or 401 (unauthorized), not 404
        assert response.status_code in [401, 403]

    def test_create_state_endpoint_exists(self, client, sample_state_data):
        """Test create state endpoint exists"""
        response = client.post("/states", json=sample_state_data)
        # Should return 403 (forbidden) or 401 (unauthorized), not 404
        assert response.status_code in [401, 403]

    def test_get_state_by_id_endpoint_exists(self, client):
        """Test get state by ID endpoint exists"""
        state_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/states/{state_id}")
        assert response.status_code in [401, 403]

    def test_invalid_state_id_format(self, client):
        """Test invalid state ID format handling"""
        response = client.get("/states/invalid-id")
        assert response.status_code in [403, 422]