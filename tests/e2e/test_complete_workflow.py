import pytest

class TestCompleteWorkflow:
    def test_hierarchical_data_workflow(self, client, sample_country_data, sample_state_data, sample_city_data):
        """Test complete hierarchical workflow: Country -> State -> City"""
        # Step 1: Verify app is running
        response = client.get("/health")
        assert response.status_code == 200, "App should be healthy"
        
        # Step 2: Try to create country (should require auth)
        response = client.post("/countries/", json=sample_country_data)
        assert response.status_code in [401, 403], "Country creation should require auth"
        
        # Step 3: Try to create state (should require auth and valid country)
        response = client.post("/states", json=sample_state_data)
        assert response.status_code in [401, 403], "State creation should require auth"
        
        # Step 4: Try to create city (should require auth and valid state)
        response = client.post("/cities", json=sample_city_data)
        assert response.status_code in [401, 403], "City creation should require auth"
        
        # Step 5: Verify all endpoints are protected consistently
        endpoints = [
            "/countries/",
            "/states",
            "/cities"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should be protected"

    def test_api_consistency_workflow(self, client):
        """Test API consistency across all modules"""
        # Test that all main endpoints exist and are consistently protected
        test_cases = [
            {"method": "GET", "url": "/countries/", "expected": [401, 403]},
            {"method": "POST", "url": "/countries/", "expected": [401, 403, 422]},
            {"method": "GET", "url": "/states", "expected": [401, 403]},
            {"method": "POST", "url": "/states", "expected": [401, 403, 422]},
            {"method": "GET", "url": "/cities", "expected": [401, 403]},
            {"method": "POST", "url": "/cities", "expected": [401, 403, 422]},
        ]
        
        for case in test_cases:
            if case["method"] == "GET":
                response = client.get(case["url"])
            elif case["method"] == "POST":
                response = client.post(case["url"], json={})
            
            assert response.status_code in case["expected"], \
                f"{case['method']} {case['url']} returned {response.status_code}, expected one of {case['expected']}"

    def test_error_handling_workflow(self, client):
        """Test error handling consistency across modules"""
        # Test invalid UUID format handling
        invalid_ids = ["invalid-id", "123", "not-a-uuid"]
        endpoints = [
            "/countries/{}",
            "/states/{}",
            "/cities/{}"
        ]
        
        for endpoint_template in endpoints:
            for invalid_id in invalid_ids:
                endpoint = endpoint_template.format(invalid_id)
                response = client.get(endpoint)
                # Should return 403 (auth) or 422 (validation), not 404 or 500
                assert response.status_code in [403, 422], \
                    f"GET {endpoint} should handle invalid ID gracefully"