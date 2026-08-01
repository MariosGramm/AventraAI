
from typing import Any
import uuid

from app import crud
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
    chat_session = crud.create_chat_session(session, current_user.id, chat_session_create_data)

    return chat_session

@router.get("/sessions", response_model=ChatSessionsPublicDTO)
def get_chats(session:SessionDep, current_user:CurrentUserDep) -> Any:
    """
    Method for chat sessions retrieval in the form of a list.
    """
    chat_sessions_query = select(ChatSession).where(col(ChatSession.owner_id == current_user.id)).order_by(ChatSession.created_at.desc())

    chat_sessions = session.exec(chat_sessions_query).all()

    return chat_sessions

@router.get("session/{chat_session_id}/messages", response_model=ChatMessagesPublicDTO)
def get_chat_session_messages(session:SessionDep, chat_session_id:uuid.UUID) -> Any:
    """
    Method for retrieving messages of a chat session.
    """
    chat_messages_query = (
        select(ChatMessage)
        .where(ChatMessage.chat_session_id == chat_session_id)
        .order_by(ChatMessage.created_at.desc())
    )

    chat_messages = session.exec(chat_messages_query).all()

    return chat_messages

@router.post("session/{chat_session_id}/send_message", response_model= ChatResponseDTO)
def send_chat_message(session:SessionDep, chat_message_create_data:ChatMessageCreateDTO, chat_session_id:uuid.UUID, current_user:CurrentUserDep) -> Any:
    """
    Method for sending a message to the agent during a chat session.
    """
    chat_session = session.get(ChatSession, chat_session_id)

    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    if chat_session.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="User is does not have enough enough privileges to send a message in this chat session")

    chat_message = crud.create_chat_message(session, chat_message_create_data, role=ChatRole.USER, chat_session_id=chat_session_id)

    #Get all the messages in the chat session to send to the agent for context.
    chat_messages = crud.get_chat_messages_by_session(session, chat_session_id)

    agent_response = run_chat_agent(chat_messages, chat_message.content)   #TODO: Implement the logic for running the chat agent and getting a response.

    agent_message = crud.create_chat_message(session, ChatMessageCreateDTO(content=agent_response), role=ChatRole.ASSISTANT, chat_session_id=chat_session_id)

    return ChatResponseDTO(
        session_id=chat_session_id,
        role=ChatRole.ASSISTANT,
        content=agent_response,
        created_at=agent_message.created_at
    )

