import pytest
from datetime import datetime
from app.models import AdminUserModel, CustomerModel, VegetableModel
from tests.fixtures.test_data import TestDataFactory

class TestModels:
    def test_admin_user_model_creation(self):
        """Test AdminUserModel creation"""
        admin = TestDataFactory.create_admin_user()
        
        assert admin.first_name == "Test"
        assert admin.last_name == "Admin"
        assert admin.email == "test@admin.com"
        assert admin.user_type == "admin"
        assert isinstance(admin.created_at, datetime)
    
    def test_customer_model_creation(self):
        """Test CustomerModel creation"""
        customer = TestDataFactory.create_customer()
        
        assert customer.first_name == "Test"
        assert customer.last_name == "Customer"
        assert customer.email == "test@customer.com"
        assert isinstance(customer.created_at, datetime)
    
    def test_vegetable_model_creation(self):
        """Test VegetableModel creation"""
        vegetable = TestDataFactory.create_vegetable()
        
        assert vegetable.name == "Test Vegetable"
        assert vegetable.price == 50.0
        assert vegetable.quantity == 100
        assert vegetable.unit_type == "kg"
    
    def test_admin_user_model_with_custom_data(self):
        """Test AdminUserModel with custom data"""
        admin = TestDataFactory.create_admin_user(
            first_name="Custom",
            email="custom@admin.com"
        )
        
        assert admin.first_name == "Custom"
        assert admin.email == "custom@admin.com"
        assert admin.last_name == "Admin"  # Default value
    
    def test_model_string_representation(self):
        """Test model string representations"""
        admin = TestDataFactory.create_admin_user()
        customer = TestDataFactory.create_customer()
        vegetable = TestDataFactory.create_vegetable()
        
        # These should not raise exceptions
        str(admin)
        str(customer)
        str(vegetable)