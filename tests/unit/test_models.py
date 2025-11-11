import pytest
from app.models import CountryModel, StateModel, CityModel, AdminUserModel

class TestModels:
    def test_country_model(self):
        """Test Country model structure"""
        assert CountryModel.__tablename__ == 'countries'
        assert hasattr(CountryModel, 'id')
        assert hasattr(CountryModel, 'name')
        assert hasattr(CountryModel, 'code')

    def test_state_model(self):
        """Test State model structure"""
        assert StateModel.__tablename__ == 'states'
        assert hasattr(StateModel, 'id')
        assert hasattr(StateModel, 'name')
        assert hasattr(StateModel, 'country_id')

    def test_city_model(self):
        """Test City model structure"""
        assert CityModel.__tablename__ == 'cities'
        assert hasattr(CityModel, 'id')
        assert hasattr(CityModel, 'name')
        assert hasattr(CityModel, 'state_id')

    def test_admin_model(self):
        """Test Admin model structure"""
        assert AdminUserModel.__tablename__ == 'admin_users'
        assert hasattr(AdminUserModel, 'id')
        assert hasattr(AdminUserModel, 'email')
        assert hasattr(AdminUserModel, 'password')