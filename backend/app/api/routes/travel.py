
from app import enums
from typing import Any
import uuid
from app import crud
from fastapi import APIRouter
from app.models import SearchSessionCreateDTO, SearchSessionPublicDTO
from app.api.deps import CurrentUserDep, SessionDep


router = APIRouter(tags=["travel"])

@router.post("/searches", response_model= SearchSessionPublicDTO)
def create_search(session:SessionDep, current_user:CurrentUserDep, search_session_create_data: SearchSessionCreateDTO) -> Any:
    """
    Method for search session creation.
    """

    search_session = crud.create_search_session(session, current_user.id, search_session_create_data)

    return search_session


    