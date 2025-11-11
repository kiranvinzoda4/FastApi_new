import pytest

class TestCountriesAPI:
    def test_get_countries_endpoint_exists(self, client):
        """Test countries endpoint exists (may be protected)"""
        response = client.get("/countries/")
        # Should return 403 (forbidden) or 401 (unauthorized), not 404
        assert response.status_code in [401, 403]

    def test_create_country_endpoint_exists(self, client, sample_country_data):
        """Test create country endpoint exists"""
        response = client.post("/countries/", json=sample_country_data)
        # Should return 403 (forbidden) or 401 (unauthorized), not 404
        assert response.status_code in [401, 403]