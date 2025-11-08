import pytest
from datetime import datetime
from app.libs.utils import (
    generate_id, now, create_password, generate_otp, 
    get_user_type, validate_email, validate_phone
)

class TestUtils:
    def test_generate_id(self):
        """Test ID generation"""
        id1 = generate_id()
        id2 = generate_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2
        assert len(id1) == 36  # UUID4 length with hyphens
    
    def test_now(self):
        """Test current datetime generation"""
        timestamp = now()
        
        assert isinstance(timestamp, datetime)
        assert timestamp <= datetime.now()
    
    def test_create_password(self):
        """Test password creation and hashing"""
        password = "TestPassword123!"
        hashed = create_password(password)
        
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0
    
    def test_generate_otp(self):
        """Test OTP generation"""
        otp = generate_otp()
        
        assert isinstance(otp, str)
        assert len(otp) == 6
        assert otp.isdigit()
    
    def test_get_user_type_admin(self):
        """Test user type detection for admin"""
        user_type = get_user_type("admin@example.com")
        assert user_type == "admin"
    
    def test_get_user_type_customer(self):
        """Test user type detection for customer"""
        user_type = get_user_type("customer@example.com")
        assert user_type == "customer"
    
    def test_validate_email_valid(self):
        """Test email validation with valid email"""
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.uk") == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid email"""
        assert validate_email("invalid-email") == False
        assert validate_email("@domain.com") == False
        assert validate_email("user@") == False
    
    def test_validate_phone_valid(self):
        """Test phone validation with valid Indian numbers"""
        assert validate_phone("9876543210") == True
        assert validate_phone("8765432109") == True
        assert validate_phone("7654321098") == True
    
    def test_validate_phone_invalid(self):
        """Test phone validation with invalid numbers"""
        assert validate_phone("1234567890") == False  # Doesn't start with 6,7,8,9
        assert validate_phone("98765432") == False    # Too short
        assert validate_phone("98765432101") == False # Too long
        assert validate_phone("abcdefghij") == False  # Non-numeric