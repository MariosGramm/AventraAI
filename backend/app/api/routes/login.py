from datetime import timedelta
from typing import Annotated, Any
from app import crud
from app.utils import generate_password_reset_token, generate_password_reset_email, send_email
from app.models import Message, Token, UserPublicDTO
from app.api.deps import CurrentUserDep, SessionDep
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings

router = APIRouter(tags=["login"])

@router.post("/login/access-token")
def login_access_token(session:SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user=crud.authenticate(session=session, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Username or password not found")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return Token(user.id, expires_delta = access_token_expires)
    
@router.post("/login/test-token", response_model= UserPublicDTO)
def test_token(current_user: CurrentUserDep) -> Any:
    """
    Test access token
    """
    return current_user

@router.post("/password-recovery/{email}")
def recover_password(email:str, session:SessionDep):
    """
    Method for password recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_password_reset_email(
            email_to = user.email, email= email, token = password_reset_token
        )

        send_email(
            email_to = user.email,
            subject = email_data.subject,
            html_content = email_data.html_content
        )

        return Message(
            message="If that email is registered, we sent a password recovery link"
        )
         

