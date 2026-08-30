from datetime import timedelta
import logging

import requests as http_requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app.utils import generate_new_account_email, send_email
from app import crud
from app.models import Token

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)

class GoogleAuthRequest(BaseModel):
    token: str

class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False

@router.post("/google", response_model=GoogleAuthResponse)
def google_auth(session: SessionDep, body: GoogleAuthRequest) -> GoogleAuthResponse:
    """
    Authenticate with Google OAuth2 access token.
    Creates a new user if not exists, or logs in existing user.
    """
    resp = http_requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {body.token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        raise HTTPException(401, "Invalid Google token")

    userinfo = resp.json()
    email = userinfo.get("email")
    google_id = userinfo.get("sub")
    given_name = userinfo.get("given_name", "")
    family_name = userinfo.get("family_name", "")

    if not email or not google_id:
        raise HTTPException(400, "Missing email or google_id from token")

    user, is_new = crud.get_or_create_google_user(
        session=session,
        email=email,
        google_id=google_id,
        first_name=given_name,
        last_name=family_name,
    )

    if not user.is_active:
        raise HTTPException(400, "Inactive user")

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    if is_new and settings.emails_enabled:
        try:
            email_data = generate_new_account_email(
                email_to=user.email,
                username=user.first_name or user.email,
            )
            send_email(
                email_to=user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        except Exception:
            logger.warning("Failed to send welcome email to %s", user.email)

    return GoogleAuthResponse(access_token=access_token, is_new_user=is_new)