import pytest
from app.libs.template_manager import (
    EmailTemplateManager, forgot_password_template, password_reset_link_template
)
class TestEmailTemplateManager:
    def test_template_manager_initialization(self):
        """Test template manager initialization"""
        manager = EmailTemplateManager()
        assert manager.env is not None
    def test_render_template_with_valid_data(self):
        """Test template rendering with valid data"""
        manager = EmailTemplateManager()
        result = manager.render_template(
            "forgot_password",
            title="Test Title",
            first_name="John",
            last_name="Doe",
            otp="123456"
        )
        assert "John" in result
        assert "Doe" in result
        assert "123456" in result
        assert "Test Title" in result
    def test_render_template_xss_protection(self):
        """Test XSS protection in template rendering"""
        manager = EmailTemplateManager()
        result = manager.render_template(
            "forgot_password",
            title="<script>alert('xss')</script>",
            first_name="<img src=x onerror=alert(1)>",
            last_name="Normal Name",
            otp="123456"
        )
        # Check that HTML is escaped
        assert "&lt;script&gt;" in result
        assert "&lt;img" in result
        assert "alert" not in result or "&lt;" in result
    def test_render_template_invalid_name(self):
        """Test template rendering with invalid template name"""
        manager = EmailTemplateManager()
        with pytest.raises(ValueError):
            manager.render_template(
                "../../../etc/passwd",  # Path traversal attempt
                title="Test",
                data="test"
            )
    def test_forgot_password_template_function(self):
        """Test forgot password template function"""
        result = forgot_password_template("John", "Doe", "123456")
        assert isinstance(result, str)
        assert "John" in result
        assert "Doe" in result
        assert "123456" in result
        assert "Password Reset" in result
    def test_password_reset_link_template_function(self):
        """Test password reset link template function"""
        result = password_reset_link_template(
            "Jane", "Smith", "https://example.com/reset?token=abc123", 30
        )
        assert isinstance(result, str)
        assert "Jane" in result
        assert "Smith" in result
        assert "https://example.com/reset?token=abc123" in result
        assert "Password Reset Request" in result
    def test_template_with_special_characters(self):
        """Test template rendering with special characters"""
        result = forgot_password_template(
            "José", 
            "García-López", 
            "123456"
        )
        assert "José" in result
        assert "García-López" in result
