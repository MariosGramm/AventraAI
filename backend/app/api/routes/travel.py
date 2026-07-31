
from app import enums
from typing import Any
import uuid
from app import crud
from fastapi import APIRouter
from app.models import SearchSession, SearchSessionCreateDTO, SearchSessionPublicDTO, SearchSessionsPublicDTO
from app.api.deps import CurrentUserDep, SessionDep
from sqlmodel import col, select


router = APIRouter(tags=["travel"])

@router.post("/searches", response_model= SearchSessionPublicDTO)
def create_search(session:SessionDep, current_user:CurrentUserDep, search_session_create_data: SearchSessionCreateDTO) -> Any:
    """
    Method for search session creation.
    """
    search_session = crud.create_search_session(session, current_user.id, search_session_create_data)

    return search_session

@router.get("/searches", response_model=SearchSessionsPublicDTO)
def get_searches(session:SessionDep, current_user:CurrentUserDep) -> Any:
    """
    Method for getting a user's search sessions.
    """
    search_session_query = (
    select(SearchSession)
    .where(SearchSession.owner_id == current_user.id)
    .order_by(col(SearchSession.created_at).desc())
    )

    search_sessions = session.exec(search_session_query).all()

    return search_sessions





    