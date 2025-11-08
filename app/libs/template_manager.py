import html
import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging

logger = logging.getLogger(__name__)

class EmailTemplateManager:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def render_template(self, template_name: str, title: str, **kwargs) -> str:
        """Render email template with automatic XSS protection"""
        try:
            # Escape all string values to prevent XSS
            safe_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    safe_kwargs[key] = html.escape(value)
                else:
                    safe_kwargs[key] = value
            
            # Load content template
            content_template = self.env.get_template(f"{template_name}.html")
            content = content_template.render(**safe_kwargs)
            
            # Load base template
            base_template = self.env.get_template("base.html")
            return base_template.render(title=title, content=content)
            
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise

# Global instance
template_manager = EmailTemplateManager()

# Template functions for backward compatibility
def forgot_password_template(first_name: str, last_name: str, otp: str) -> str:
    return template_manager.render_template(
        "forgot_password",
        title="Password Reset",
        first_name=first_name,
        last_name=last_name,
        otp=otp
    )

def send_password_template(first_name: str, last_name: str, password: str) -> str:
    return template_manager.render_template(
        "send_password", 
        title="Your Account Password",
        first_name=first_name,
        last_name=last_name,
        password=password
    )