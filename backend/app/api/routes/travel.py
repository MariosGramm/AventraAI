
from app import enums
from typing import Any
import uuid
from app import crud
from fastapi import APIRouter, HTTPException
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
    search_sessions_query = (
    select(SearchSession)
    .where(SearchSession.owner_id == current_user.id)
    .order_by(col(SearchSession.created_at).desc())
    )

    search_sessions = session.exec(search_sessions_query).all()

    return search_sessions

@router.get("/searches/{search_session_id}", response_model=SearchSessionPublicDTO)
def get_search(session:SessionDep, search_session_id:uuid.UUID, current_user: CurrentUserDep):
    """
    Method for getting a specific session using a search session id with search session content.
    """
    if search_session.owner_id != current_user.id:
        raise HTTPException(403, "User does not have enough privileges")
    
    search_session_query = (
        select(SearchSession)
        .where(SearchSession.id == search_session_id)
    )

    search_session = session.exec(search_session_query).first()

    if not search_session:
        raise HTTPException(404, "Search session not found")

    return search_session









    