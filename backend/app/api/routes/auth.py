from datetime import timedelta

import requests as http_requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app import crud
from app.models import Token

router = APIRouter(tags=["auth"])

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

    return GoogleAuthResponse(access_token=access_token, is_new_user=is_new)