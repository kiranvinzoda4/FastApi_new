import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Generator
from contextlib import contextmanager
from app.config import settings
from app.core.error_handler import handle_errors
class EmailService:
    def __init__(self) -> None:
        self.smtp_host: str = settings.SMTP_HOST
        self.smtp_port: int = settings.SMTP_PORT
        self.smtp_user: str = settings.SMTP_USER
        self.smtp_password: str = settings.SMTP_PASSWORD
    @contextmanager
    def _get_smtp_connection(self) -> Generator[smtplib.SMTP, None, None]:
        """Context manager for SMTP connection"""
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        if self.smtp_user and self.smtp_password:
            server.login(self.smtp_user, self.smtp_password)
        try:
            yield server
        finally:
            server.quit()
    @handle_errors
    def send_email(
        self, 
        recipients: List[str], 
        subject: str, 
        html_body: str,
        attach_logo: bool = True
    ) -> bool:
        """Send an email to the specified recipients"""
        if not self.smtp_user or not self.smtp_password:
            raise ValueError("Email credentials not configured")
        if not recipients:
            raise ValueError("No recipients specified")
        msg = MIMEMultipart("related")
        msg["From"] = self.smtp_user
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, "html"))
        if attach_logo:
            self._attach_logo(msg)
        with self._get_smtp_connection() as server:
            server.sendmail(self.smtp_user, recipients, msg.as_string())
        return True
    def _attach_logo(self, msg: MIMEMultipart) -> None:
        """Attach logo image to email"""
        logo_path = os.path.join("app", "static", "images", "logo", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                img_data = img_file.read()
                if img_data:
                    img = MIMEImage(img_data)
                    img.add_header("Content-ID", "<logo_image>")
                    msg.attach(img)
# Global email service instance
email_service = EmailService()
# Backward compatibility function
def send_email(recipients: List[str], subject: str, html_body: str) -> bool:
    return email_service.send_email(recipients, subject, html_body)
