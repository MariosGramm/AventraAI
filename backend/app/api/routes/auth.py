# api/routes/auth.py
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
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

@router.post("/google", response_model=Token)
def google_auth(session: SessionDep, body: GoogleAuthRequest) -> Token:
    """
    Authenticate with Google OAuth2 ID token.
    Creates a new user if not exists, or logs in existing user.
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            body.token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(401, f"Invalid Google token: {e}")

    email     = idinfo.get("email")
    google_id = idinfo.get("sub")
    full_name = idinfo.get("name")

    if not email or not google_id:
        raise HTTPException(400, "Missing email or google_id from token")

    # Get or create user
    user = crud.get_or_create_google_user(
        session=session,
        email=email,
        google_id=google_id,
        full_name=full_name
    )

    if not user.is_active:
        raise HTTPException(400, "Inactive user")

    access_token = create_access_token(subject=str(user.id)) #authenticated

    return Token(access_token=access_token)