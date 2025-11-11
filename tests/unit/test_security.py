import pytest
from unittest.mock import patch
from app.security import hash_password, verify_password, generate_otp, create_access_token, verify_access_token

class TestSecurity:
    def test_hash_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password(self):
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) == True
        assert verify_password("wrongpassword", hashed) == False

    def test_generate_otp(self):
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
        
        otp_custom = generate_otp(4)
        assert len(otp_custom) == 4

    def test_create_access_token(self, mock_settings):
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 50