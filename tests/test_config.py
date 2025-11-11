def test_config_loading():
    """Test configuration loads properly"""
    from app.config import settings
    
    # Basic config should be loaded
    assert hasattr(settings, 'DEBUG')
    assert hasattr(settings, 'DB_HOST')
    assert hasattr(settings, 'ACCESS_JWT_KEY')

def test_database_models():
    """Test database models are defined"""
    from app.models import CountryModel, StateModel, CityModel, AdminUserModel
    
    # Models should be importable
    assert CountryModel.__tablename__ == 'countries'
    assert StateModel.__tablename__ == 'states' 
    assert CityModel.__tablename__ == 'cities'
    assert AdminUserModel.__tablename__ == 'admin_users'