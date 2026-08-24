
import logging
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
logger = logging.getLogger(__name__)

MAX_PINNED_CHAT_SESSIONS = 3

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

@router.get("/session/{chat_session_id}/messages", response_model=ChatMessagesPublicDTO)
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
        logger.exception("Agent pipeline failed for chat session %s", chat_session_id)
        agent_chat_response = (
            "I'm having trouble processing your request right now. "
            "Please try again in a moment."
        )

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

    if not chat_session.is_pinned:
        pinned_count = len(session.exec(
            select(ChatSession)
            .where(ChatSession.owner_id == current_user.id)
            .where(ChatSession.is_pinned == True)  # noqa: E712
        ).all())
        if pinned_count >= MAX_PINNED_CHAT_SESSIONS:
            raise HTTPException(400, f"You can pin up to {MAX_PINNED_CHAT_SESSIONS} chats")

    chat_session.is_pinned = not chat_session.is_pinned
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


@router.post("/session/{chat_session_id}/generate_title", response_model=ChatSessionPublicDTO)
def generate_chat_title(
    session: SessionDep,
    chat_session_id: uuid.UUID,
    current_user: CurrentUserDep,
) -> Any:
    """Auto-generate a chat session title from the first user message."""
    chat_session = session.get(ChatSession, chat_session_id)
    if not chat_session:
        raise HTTPException(404, "Chat session not found")
    if chat_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")

    first_message = session.exec(
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .where(ChatMessage.role == ChatRole.USER)
        .order_by(ChatMessage.created_at)
    ).first()

    if not first_message:
        raise HTTPException(400, "No user messages in this session")

    try:
        pipeline = TravelAgentPipeline()
        title = pipeline.generate_title(first_message.content)
    except Exception:
        logger.exception("Title generation failed for session %s", chat_session_id)
        title = first_message.content[:50]

    chat_session.title = title
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


    

