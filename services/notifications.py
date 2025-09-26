# services/notifications.py
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email_notification(to_email, subject, body):
    """
    Sends an email via Gmail SMTP.
    Returns True if successful, False otherwise.
    """
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg.set_content(body)

        print("🔐 Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            print(f"✅ Logged in as {EMAIL_USER}")
            smtp.send_message(msg)
            print(f"📨 Sent message to {to_email}")

        return True
    except Exception as e:
        print("❌ Email failed:", e)
        return False
