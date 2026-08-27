
import logging
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
import uuid

from pydantic import BaseModel
from app import crud
from app.agent.agent_pipeline import TravelAgentPipeline
from app.api.deps import CurrentUserDep, SessionDep
from app.enums import ChatRole, SubscriptionTier
from app.models import ChatMessage, ChatMessageCreateDTO, ChatMessagesPublicDTO, ChatResponseDTO, ChatSession, ChatSessionCreateDTO, ChatSessionPublicDTO, ChatSessionsPublicDTO, User
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, col, select
from dateutil.relativedelta import relativedelta


router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)

MAX_PINNED_CHAT_SESSIONS = 3
FREE_MESSAGE_LIMIT = 50
PAID_MESSAGE_LIMIT = 500


def _check_message_limit(session: SessionDep, current_user: CurrentUserDep) -> None:
    """Check chat message quota and reset if needed. Raises 429 if limit reached."""
    if current_user.is_superuser:
        return

    now = datetime.now(UTC)

    if (current_user.searches_reset_date is None or now >= current_user.searches_reset_date):
        current_user.monthly_messages_used = 0
        current_user.monthly_searches_used = 0
        current_user.searches_reset_date = now + relativedelta(months=1)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)

    if current_user.subscription_tier == SubscriptionTier.FREE:
        if current_user.monthly_messages_used >= FREE_MESSAGE_LIMIT:
            raise HTTPException(429, f"Monthly message limit of {FREE_MESSAGE_LIMIT} reached. Upgrade to Pro for more messages.")
    elif current_user.subscription_tier == SubscriptionTier.PAID:
        if current_user.monthly_messages_used >= PAID_MESSAGE_LIMIT:
            raise HTTPException(429, f"Monthly message limit of {PAID_MESSAGE_LIMIT} reached. Your limit resets next month.")

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

    _check_message_limit(session, current_user)

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

    current_user.monthly_messages_used += 1
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

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


class _SaveMessageDTO(BaseModel):
    role: str
    content: str

@router.post("/session/{chat_session_id}/save_message")
def save_chat_message(
    session: SessionDep,
    chat_session_id: uuid.UUID,
    current_user: CurrentUserDep,
    data: _SaveMessageDTO,
) -> dict:
    """Save a message to a chat session without triggering the agent."""
    chat_session = session.get(ChatSession, chat_session_id)
    if not chat_session:
        raise HTTPException(404, "Chat session not found")
    if chat_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")
    crud.create_chat_message(
        session=session,
        chat_creation_data=ChatMessageCreateDTO(content=data.content),
        role=ChatRole(data.role),
        chat_session_id=chat_session_id,
    )
    return {"status": "ok"}


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


@router.delete("/session/{chat_session_id}", status_code=204)
def delete_chat_session(
    session: SessionDep,
    chat_session_id: uuid.UUID,
    current_user: CurrentUserDep,
) -> None:
    """Permanently delete a chat session and all of its messages."""
    chat_session = session.get(ChatSession, chat_session_id)
    if not chat_session:
        raise HTTPException(404, "Chat session not found")
    if chat_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")

    crud.delete_chat_session(session=session, chat_session=chat_session)


class _RenameDTO(BaseModel):
    title: str

@router.patch("/session/{chat_session_id}/rename", response_model=ChatSessionPublicDTO)
def rename_chat_session(
    session: SessionDep,
    chat_session_id: uuid.UUID,
    current_user: CurrentUserDep,
    data: _RenameDTO,
) -> Any:
    """Rename a chat session."""
    chat_session = session.get(ChatSession, chat_session_id)
    if not chat_session:
        raise HTTPException(404, "Chat session not found")
    if chat_session.owner_id != current_user.id:
        raise HTTPException(403, "Not enough privileges")
    chat_session.title = data.title[:100]
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session


class _GuestHistoryMessage(BaseModel):
    role: str
    content: str

class GuestChatRequestDTO(BaseModel):
    content: str
    history: list[_GuestHistoryMessage] = []

@router.post("/guest/send_message")
def guest_send_message(data: GuestChatRequestDTO) -> dict:
    """Guest chat endpoint — no authentication required."""
    history = [
        SimpleNamespace(role=ChatRole(msg.role), content=msg.content)
        for msg in data.history
    ]

    dummy_user = User(
        first_name="Guest", last_name="User",
        email="guest@aventraai.com", hashed_password="",
        subscription_tier=SubscriptionTier.FREE,
    )

    try:
        pipeline = TravelAgentPipeline()
        response = pipeline.run_chat(data.content, history, dummy_user)
    except Exception:
        logger.exception("Guest agent pipeline failed")
        response = "I'm having trouble right now. Please try again."

    return {"content": response, "created_at": datetime.now(UTC).isoformat()}


    

