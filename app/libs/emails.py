import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Optional
from contextlib import contextmanager
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
    
    @contextmanager
    def _get_smtp_connection(self):
        """Context manager for SMTP connection"""
        server = None
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            yield server
        except Exception as e:
            logger.error(f"SMTP connection error: {e}")
            raise
        finally:
            if server:
                try:
                    server.quit()
                except Exception as e:
                    logger.warning(f"Error closing SMTP connection: {e}")
    
    def send_email(
        self, 
        recipients: List[str], 
        subject: str, 
        html_body: str,
        attach_logo: bool = True
    ) -> bool:
        """
        Send an email to the specified recipients.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            html_body: HTML email body content
            attach_logo: Whether to attach logo image
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("Email credentials not configured")
            return False
        
        if not recipients:
            logger.warning("No recipients specified")
            return False
        
        try:
            msg = MIMEMultipart("related")
            msg["From"] = self.smtp_user
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            
            msg_alternative = MIMEMultipart("alternative")
            msg.attach(msg_alternative)
            msg_alternative.attach(MIMEText(html_body, "html"))
            
            # Attach logo image if requested
            if attach_logo:
                self._attach_logo(msg)
            
            # Send email
            with self._get_smtp_connection() as server:
                server.sendmail(self.smtp_user, recipients, msg.as_string())
            
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _attach_logo(self, msg: MIMEMultipart) -> None:
        """Attach logo image to email"""
        logo_path = os.path.join("app", "static", "images", "logo", "logo.png")
        try:
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header("Content-ID", "<logo_image>")
                    msg.attach(img)
            else:
                logger.warning(f"Logo image not found at {logo_path}")
        except Exception as e:
            logger.error(f"Error attaching logo: {e}")

# Global email service instance
email_service = EmailService()

# Backward compatibility function
def send_email(recipients: List[str], subject: str, html_body: str) -> bool:
    return email_service.send_email(recipients, subject, html_body)
