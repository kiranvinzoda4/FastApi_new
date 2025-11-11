import uuid
from datetime import datetime
from app.models import AdminUserModel, CustomerModel, VegetableModel
from app.libs.utils import create_password


class TestDataFactory:
    @staticmethod
    def create_admin_user(**kwargs):
        defaults = {
            "id": str(uuid.uuid4()),
            "first_name": "Test",
            "last_name": "Admin",
            "email": "test@admin.com",
            "phone": "9876543210",
            "password": create_password("TestPass123!"),
            "user_type": "admin",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        defaults.update(kwargs)
        return AdminUserModel(**defaults)

    @staticmethod
    def create_customer(**kwargs):
        defaults = {
            "id": str(uuid.uuid4()),
            "first_name": "Test",
            "last_name": "Customer",
            "email": "test@customer.com",
            "phone": "9876543211",
            "password": create_password("TestPass123!"),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        defaults.update(kwargs)
        return CustomerModel(**defaults)

    @staticmethod
    def create_vegetable(**kwargs):
        defaults = {
            "id": str(uuid.uuid4()),
            "name": "Test Vegetable",
            "description": "Test description",
            "price": 50.0,
            "quantity": 100,
            "unit_type": "kg",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        defaults.update(kwargs)
        return VegetableModel(**defaults)
