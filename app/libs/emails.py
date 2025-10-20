import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

def send_email(recipients: list, subject: str, html_body: str) -> bool:
    sender_email = "kiranvinzoda5@gmail.com"
    app_password = "txzt ibrn zatq omjc"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    try:
        msg = MIMEMultipart("related")
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)

        msg_alternative.attach(MIMEText(html_body, "html"))

        # Attach logo image
        logo_path = os.path.join("app", "static", "images", "logo", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                img = MIMEImage(img_file.read())
                img.add_header("Content-ID", "<logo_image>")
                msg.attach(img)
        else:
            print("Logo image not found at", logo_path)

        # Send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False
