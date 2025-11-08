import pytest
from app.security import SecurityUtils
from app.exceptions import AuthenticationException

class TestSecurityUtils:
    def test_hash_password(self):
        """Test password hashing"""
        password = "<test_password>"
        hashed = SecurityUtils.hash_password(password)
        
        assert hashed != password
        assert SecurityUtils.verify_password(password, hashed)
    
    def test_verify_password_invalid(self):
        """Test password verification with wrong password"""
        # amazonq-ignore-next-line
        password = "<test_password>"
        wrong_password = "<wrong_password>"
        hashed = SecurityUtils.hash_password(password)
        
        assert not SecurityUtils.verify_password(wrong_password, hashed)
    
    def test_generate_otp(self):
        """Test OTP generation"""
        otp = SecurityUtils.generate_otp()
        
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_generate_otp_custom_length(self):
        """Test OTP generation with custom length"""
        otp = SecurityUtils.generate_otp(8)
        
        assert len(otp) == 8
        assert otp.isdigit()
    
    def test_generate_secure_token(self):
        """Test secure token generation"""
        token = SecurityUtils.generate_secure_token()
        
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "<user_id>", "email": "<email>"}
        token = SecurityUtils.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "<user_id>", "email": "<email>"}
        token = SecurityUtils.create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_access_token(self):
        """Test access token verification"""
        data = {"sub": "<user_id>", "email": "<email>"}
        token = SecurityUtils.create_access_token(data)
        
        payload = SecurityUtils.verify_token(token, "access")
        
        assert payload["sub"] == "<user_id>"
        assert payload["email"] == "<email>"
        assert payload["type"] == "access"
    
    def test_verify_refresh_token(self):
        """Test refresh token verification"""
        data = {"sub": "<user_id>", "email": "<email>"}
        token = SecurityUtils.create_refresh_token(data)
        
        payload = SecurityUtils.verify_token(token, "refresh")
        
        assert payload["sub"] == "<user_id>"
        assert payload["email"] == "<email>"
        assert payload["type"] == "refresh"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        with pytest.raises(AuthenticationException):
            SecurityUtils.verify_token("invalid_token", "access")
    
    def test_verify_token_wrong_type(self):
        """Test token verification with wrong token type"""
        data = {"sub": "<user_id>", "email": "<email>"}
        access_token = SecurityUtils.create_access_token(data)
        
        with pytest.raises(AuthenticationException):
            SecurityUtils.verify_token(access_token, "refresh")
    
    def test_hash_api_key(self):
        """Test API key hashing"""
        api_key = "<test_api_key>"
        hashed = SecurityUtils.hash_api_key(api_key)
        
        assert hashed != api_key
        assert len(hashed) == 64  # SHA256 hex digest length