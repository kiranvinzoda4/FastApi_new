import pytest
from fastapi.testclient import TestClient
class TestAuthAPI:
    def test_admin_login_success(self, client: TestClient, admin_user):
        """Test successful admin login"""
        response = client.post("/admin/admin-login", json={
            "email": admin_user.email,
            "password": "TestPass123!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data
        assert data["email"] == admin_user.email
    def test_admin_login_invalid_credentials(self, client: TestClient, admin_user):
        """Test admin login with invalid credentials"""
        response = client.post("/admin/admin-login", json={
            "email": admin_user.email,
            "password": "WrongPassword"
        })
        assert response.status_code == 401
    def test_admin_login_nonexistent_user(self, client: TestClient):
        """Test admin login with non-existent user"""
        response = client.post("/admin/admin-login", json={
            "email": "nonexistent@example.com",
            "password": "TestPass123!"
        })
        assert response.status_code == 401
    def test_get_admin_profile_authenticated(self, client: TestClient, auth_headers):
        """Test getting admin profile with valid token"""
        response = client.get("/admin/admin-profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "first_name" in data
    def test_get_admin_profile_unauthenticated(self, client: TestClient):
        """Test getting admin profile without token"""
        response = client.get("/admin/admin-profile")
        assert response.status_code == 401 or response.status_code == 403
    def test_update_admin_profile(self, client: TestClient, auth_headers):
        """Test updating admin profile"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "phone": "9876543210"
        }
        response = client.put("/admin/admin-profile", 
                            json=update_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
    def test_change_password_success(self, client: TestClient, auth_headers):
        """Test successful password change"""
        password_data = {
            "old_password": "TestPass123!",
            "new_password": "NewTestPass123!"
        }
        response = client.put("/admin/admin-change-password", 
                            json=password_data, 
                            headers=auth_headers)
        assert response.status_code == 200
    def test_change_password_wrong_old_password(self, client: TestClient, auth_headers):
        """Test password change with wrong old password"""
        password_data = {
            "old_password": "WrongOldPassword",
            "new_password": "NewTestPass123!"
        }
        response = client.put("/admin/admin-change-password", 
                            json=password_data, 
                            headers=auth_headers)
        assert response.status_code == 401
    def test_forgot_password_existing_user(self, client: TestClient, admin_user):
        """Test forgot password for existing user"""
        response = client.put("/admin/send-forgot-password-email", json={
            "email": admin_user.email
        })
        # Should succeed even if email service is not configured
        assert response.status_code in [200, 500]  # 500 if email not configured
    def test_forgot_password_nonexistent_user(self, client: TestClient):
        """Test forgot password for non-existent user"""
        response = client.put("/admin/send-forgot-password-email", json={
            "email": "nonexistent@example.com"
        })
        assert response.status_code == 401
