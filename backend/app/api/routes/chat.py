
from typing import Any

from app import crud
from app.api.deps import CurrentUserDep
from app.models import ChatSession, ChatSessionCreateDTO, ChatSessionPublicDTO, ChatSessionsPublicDTO
from fastapi import APIRouter
from sqlmodel import Session, col, select


router = APIRouter(tags=["chat"])

@router.post("/session", response_model=ChatSessionPublicDTO)
def create_chat(session:Session, current_user:CurrentUserDep, chat_session_create_data:ChatSessionCreateDTO) -> Any:
    """
    Method for chat session creation.
    """
    chat_session = crud.create_chat_session(session, current_user.id, chat_session_create_data)

    return chat_session

@router.get("/sessions", response_model=ChatSessionsPublicDTO)
def get_chats(session:Session, current_user:CurrentUserDep) -> Any:
    """
    Method for chat sessions retrieval.
    """
    chat_sessions_query = select(ChatSession).where(col(ChatSession.owner_id == current_user.id)).order_by(ChatSession.created_at.desc())

    chat_sessions = session.exec(chat_sessions_query).all()

    return chat_sessions