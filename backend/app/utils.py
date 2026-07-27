from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.core import security
from app.core.security import settings
from jinja2 import Template
import jwt


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

    

    