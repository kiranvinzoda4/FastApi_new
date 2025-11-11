import os
from jinja2 import Environment, FileSystemLoader
from app.core.error_handler import handle_errors


class EmailTemplateManager:
    def __init__(self):
        template_dir = os.path.join(
            os.path.dirname(__file__), "..", "templates", "email"
        )
        self.env = Environment(loader=FileSystemLoader(template_dir))

    @handle_errors
    def render_template(self, template_name: str, **kwargs) -> str:
        template = self.env.get_template(f"{template_name}.html")
        return template.render(**kwargs)


template_manager = EmailTemplateManager()


@handle_errors
def forgot_password_template(first_name: str, last_name: str, otp: str) -> str:
    return template_manager.render_template(
        "forgot_password", first_name=first_name, last_name=last_name, otp=otp
    )


@handle_errors
def password_reset_link_template(
    first_name: str, last_name: str, reset_link: str, expiry_minutes: int = 30
) -> str:
    return template_manager.render_template(
        "password_reset_link",
        first_name=first_name,
        last_name=last_name,
        reset_link=reset_link,
        expiry_minutes=expiry_minutes,
    )
