from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core import security
from app.core.security import settings
import emails
from jinja2 import Template
import jwt
import logging

import resend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str

def render_email_template(*, email_template_name:str, context:dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / email_template_name
    ).read_text()

    html_content = Template(template_str).render(context)
    return html_content


def generate_password_reset_token(email:str) -> str:
    """
    Method for password reset token generation.
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp":exp, "nbf":now, "sub":email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM
    )

    return encoded_jwt

def generate_password_reset_email(email_to: str, email: str, token: str) -> EmailData:
    """
    Method for password reset email generation.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password Reset Request"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #7F77DD;">{project_name}</h1>
        </div>
        <h2 style="color: #26215C;">Reset your password</h2>
        <p style="color: #6c757d; line-height: 1.8;">
            We received a request to reset the password for your account 
            associated with <strong>{email_to}</strong>.
        </p>
        <p style="color: #6c757d; line-height: 1.8;">
            Click the button below to reset your password. 
            This link will expire in <strong>{settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS} hours</strong>.
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link}" 
               style="background: #7F77DD; color: white; padding: 12px 32px; 
                      border-radius: 8px; text-decoration: none; font-weight: 500;">
                Reset Password →
            </a>
        </div>
        <div style="background: #EEEDFE; border-radius: 12px; padding: 20px; margin: 20px 0;">
            <p style="color: #534AB7; margin: 0; font-size: 13px;">
                If you did not request a password reset, you can safely ignore this email. 
                Your password will not be changed.
            </p>
        </div>
        <p style="color: #6c757d; font-size: 12px; margin-top: 30px; text-align: center;">
            © 2026 {project_name} · 
            <a href="{settings.FRONTEND_HOST}/privacy" style="color: #7F77DD;">Privacy</a> · 
            <a href="{settings.FRONTEND_HOST}/terms" style="color: #7F77DD;">Terms</a>
        </p>
    </body>
    </html>
    """
    return EmailData(html_content=html_content, subject=subject)

def generate_new_account_email(email_to: str, username: str) -> EmailData:
    """
    Method for new account welcome email generation.
    """
    project_name = settings.PROJECT_NAME
    subject = f"Welcome to {project_name}!"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #7F77DD;">{project_name}</h1>
        </div>
        <h2 style="color: #26215C;">Welcome aboard, {username}!</h2>
        <p style="color: #6c757d; line-height: 1.8;">
            Your account has been created successfully. 
            You're now ready to start planning your next adventure with AI.
        </p>
        <div style="background: #EEEDFE; border-radius: 12px; padding: 20px; margin: 20px 0;">
            <p style="color: #534AB7; margin: 0;">
                <strong>Account:</strong> {email_to}
            </p>
        </div>
        <div style="text-align: center; margin-top: 30px;">
            <a href="{settings.FRONTEND_HOST}/chat" 
               style="background: #7F77DD; color: white; padding: 12px 32px; 
                      border-radius: 8px; text-decoration: none; font-weight: 500;">
                Start Planning →
            </a>
        </div>
        <p style="color: #6c757d; font-size: 12px; margin-top: 30px; text-align: center;">
            © 2026 {project_name} · 
            <a href="{settings.FRONTEND_HOST}/privacy" style="color: #7F77DD;">Privacy</a> · 
            <a href="{settings.FRONTEND_HOST}/terms" style="color: #7F77DD;">Terms</a>
        </p>
    </body>
    </html>
    """
    return EmailData(html_content=html_content, subject=subject)

def send_email(*, email_to: str, subject: str = "", html_content: str = "") -> None:
    """
    Method for sending emails via Resend.
    """
    resend.api_key = settings.RESEND_API_KEY
    
    try:
        response = resend.Emails.send({
            "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
            "to": email_to,
            "subject": subject,
            "html": html_content
        })
        logger.info(f"Email sent successfully to {email_to} — ID: {response.get('id')}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")
        raise

def verify_password_reset_token(token:str) -> str | None:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])

        return str(decoded_token["sub"])
    except jwt.InvalidTokenError:
        return None




    