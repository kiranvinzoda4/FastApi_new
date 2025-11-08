import html
import os
import re
from typing import Dict, Any, Set
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template, SandboxedEnvironment
import logging

logger = logging.getLogger(__name__)

class EmailTemplateManager:
    def __init__(self) -> None:
        template_dir: str = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.env: Environment = SandboxedEnvironment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render_template(self, template_name: str, title: str, **kwargs) -> str:
        """Render email template with automatic XSS protection"""
        try:
            # Validate template name to prevent path traversal and injection
            if not re.match(r'^[a-zA-Z0-9_-]+$', template_name):
                raise ValueError("Invalid template name")
            
            # Additional security: whitelist allowed templates (removed send_password for security)
            allowed_templates: Set[str] = {'forgot_password', 'password_reset_link'}
            if template_name not in allowed_templates:
                raise ValueError(f"Template '{template_name}' not allowed")
            
            # Escape all string values to prevent XSS
            safe_kwargs: Dict[str, Any] = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    safe_kwargs[key] = html.escape(value)
                else:
                    safe_kwargs[key] = value
            
            # Load content template with sandboxed execution
            content_template: Template = self.env.get_template(f"{template_name}.html")
            # Render in sandboxed environment to prevent code execution
            content: str = content_template.render(**safe_kwargs)
            
            # Load base template
            base_template: Template = self.env.get_template("base.html")
            return base_template.render(title=html.escape(title), content=content)
            
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise ValueError(f"Template rendering failed: {str(e)}")

# Global instance
template_manager = EmailTemplateManager()

# Template functions for backward compatibility
def forgot_password_template(first_name: str, last_name: str, otp: str) -> str:
    try:
        return template_manager.render_template(
            "forgot_password",
            title="Password Reset",
            first_name=first_name,
            last_name=last_name,
            otp=otp
        )
    except Exception as e:
        logger.error(f"Error rendering forgot password template: {e}")
        raise

# SECURITY: send_password_template removed - sending passwords via email is insecure
# Use password_reset_link_template instead for secure password reset flow

def password_reset_link_template(first_name: str, last_name: str, reset_link: str, expiry_minutes: int = 30) -> str:
    try:
        return template_manager.render_template(
            "password_reset_link",
            title="Password Reset Request",
            first_name=first_name,
            last_name=last_name,
            reset_link=reset_link,
            expiry_minutes=expiry_minutes
        )
    except Exception as e:
        logger.error(f"Error rendering password reset link template: {e}")
        raise