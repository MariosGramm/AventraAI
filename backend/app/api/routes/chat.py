
from typing import Any
import uuid

from app import crud
from app.agent.agent_pipeline import TravelAgentPipeline
from app.api.deps import CurrentUserDep, SessionDep
from app.enums import ChatRole
from app.models import ChatMessage, ChatMessageCreateDTO, ChatMessagesPublicDTO, ChatResponseDTO, ChatSession, ChatSessionCreateDTO, ChatSessionPublicDTO, ChatSessionsPublicDTO
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, col, select


router = APIRouter(tags=["chat"])

@router.post("/session", response_model=ChatSessionPublicDTO)
def create_chat(session:SessionDep, current_user:CurrentUserDep, chat_session_create_data:ChatSessionCreateDTO) -> Any:
    """
    Method for chat session creation.
    """
    chat_session = crud.create_chat_session(session=session, owner_id=current_user.id, chat_session_creation_data=chat_session_create_data)

    return chat_session

@router.get("/sessions", response_model=ChatSessionsPublicDTO)
def get_chats(session:SessionDep, current_user:CurrentUserDep) -> Any:
    """
    Method for chat sessions retrieval in the form of a list.
    """
    chat_sessions_query = select(ChatSession).where(ChatSession.owner_id == current_user.id).order_by(ChatSession.created_at.desc())

    chat_sessions = session.exec(chat_sessions_query).all()

    return ChatSessionsPublicDTO(chat_sessions=chat_sessions, count=len(chat_sessions))

@router.get("session/{chat_session_id}/messages", response_model=ChatMessagesPublicDTO)
def get_chat_session_messages(session:SessionDep, chat_session_id:uuid.UUID, current_user:CurrentUserDep) -> Any:
    """
    Method for retrieving messages of a chat session.
    """
    chat_session = session.get(ChatSession, chat_session_id)
    if not chat_session:
        raise HTTPException(404, "Chat session not found")
    if chat_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")

    chat_messages_query = (
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .order_by(ChatMessage.created_at.desc())
    )

    chat_messages = session.exec(chat_messages_query).all()

    return ChatMessagesPublicDTO(data=chat_messages, count=len(chat_messages))

@router.post("/session/{chat_session_id}/send_message", response_model= ChatResponseDTO)
def send_chat_message(session:SessionDep, chat_message_create_data:ChatMessageCreateDTO, chat_session_id:uuid.UUID, current_user:CurrentUserDep) -> Any:
    """
    Method for sending a message to the agent during a chat session.
    """
    chat_session = session.get(ChatSession, chat_session_id)

    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    if chat_session.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="User is does not have enough enough privileges to send a message in this chat session")

    chat_message = crud.create_chat_message(session=session, chat_creation_data=chat_message_create_data, role=ChatRole.USER, chat_session_id=chat_session_id)

    # Load chat history - needed for accurate response from the agent
    chat_history = crud.get_chat_messages_by_session(session=session, chat_session_id=chat_session_id)

    try:
        # Run agent pipeline -> Chat Mode (run_chat method)
        agent_pipeline = TravelAgentPipeline()
        agent_chat_response = agent_pipeline.run_chat(chat_message.content, chat_history, current_user)
    except Exception as e:
        raise HTTPException(500, f"Agent pipeline failed:{e}")

    agent_message = crud.create_chat_message(session=session, chat_creation_data=ChatMessageCreateDTO(content=agent_chat_response), role=ChatRole.ASSISTANT, chat_session_id=chat_session_id)

    return ChatResponseDTO(
        session_id=chat_session_id,
        role=ChatRole.ASSISTANT,
        content=agent_chat_response,
        created_at=agent_message.created_at
    )

@router.patch("/session/{chat_session_id}/pin")
def pin_chat_session(
    session: SessionDep,
    chat_session_id: uuid.UUID,
    current_user: CurrentUserDep
) -> ChatSessionPublicDTO:
    """Pin or unpin a chat session."""
    chat_session = session.get(ChatSession, chat_session_id)
    if not chat_session:
        raise HTTPException(404, "Chat session not found")
    if chat_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")

    chat_session.is_pinned = not chat_session.is_pinned
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session 


    

