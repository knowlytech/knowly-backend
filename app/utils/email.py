import smtplib
from email.message import EmailMessage
import os

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Knowly Email Verification OTP"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = to_email

    msg.set_content(f"""
Your Knowly verification OTP is: {otp}

This OTP is valid for 5 minutes.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            os.getenv("SMTP_EMAIL"),
            os.getenv("SMTP_PASSWORD")
        )
        server.send_message(msg)
