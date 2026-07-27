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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str

def render_email_template(*, email_template_name:str, context:dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / email_template_name
    ).read_text

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

def generate_password_reset_email(email_to:str, email:str, token:str) -> EmailData:
    """
    Method for password reset email generation.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        email_template_name="reset_password.html",
        context= {
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )

    return EmailData(html_content=html_content, subject=subject)

def generate_new_account_email(email_to:str, username:str, password:str) -> EmailData:
    """
    Method for new account email generation.
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        email_template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link":settings.FRONTEND_HOST
        }
    )

    return EmailData(html_content= html_content, subject= subject)

def send_email(*, email_to:str, subject:str = "", html_content:str = ""):
    """
    Method for sending emails.
    """
    assert settings.emails_enabled, "No provided configuration for email variables"

    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)
    )

    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "tls": settings.SMTP_TLS
    }

    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"Send email result: {response}")




    