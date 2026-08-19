from collections.abc import Generator
from typing import Annotated
from jwt import InvalidTokenError
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlmodel import Session

# Get token endpoint
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    
    user = session.get(User, token_data.sub)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive")

    return user
    
CurrentUserDep = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(current_user:CurrentUserDep) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="User does not have enough privileges"
        )
    return current_user
