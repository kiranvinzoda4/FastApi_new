import smtplib
from email.mime.text import MIMEText
from typing import List
from app.config import settings
from app.core.error_handler import handle_errors

@handle_errors
def send_email(recipients: List[str], subject: str, html_body: str) -> bool:
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise ValueError("Email credentials not configured")
    
    if not recipients:
        raise ValueError("No recipients specified")
    
    msg = MIMEText(html_body, "html")
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, recipients, msg.as_string())
    
    return True