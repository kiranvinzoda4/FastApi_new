import pytest

class TestCitiesAPI:
    def test_get_cities_endpoint_exists(self, client):
        """Test cities endpoint exists (may be protected)"""
        response = client.get("/cities")
        # Should return 403 (forbidden) or 401 (unauthorized), not 404
        assert response.status_code in [401, 403]

    def test_create_city_endpoint_exists(self, client, sample_city_data):
        """Test create city endpoint exists"""
        response = client.post("/cities", json=sample_city_data)
        # Should return 403 (forbidden) or 401 (unauthorized), not 404
        assert response.status_code in [401, 403]

    def test_get_city_by_id_endpoint_exists(self, client):
        """Test get city by ID endpoint exists"""
        city_id = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/cities/{city_id}")
        assert response.status_code in [401, 403]

    def test_invalid_city_id_format(self, client):
        """Test invalid city ID format handling"""
        response = client.get("/cities/invalid-id")
        assert response.status_code in [403, 422]