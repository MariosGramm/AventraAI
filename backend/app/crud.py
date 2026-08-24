import uuid

from app.core.security import get_password_hash, verify_password
from app.enums import AgentStep, AuthProvider, ChatRole, SearchSessionStatus, SubscriptionTier
from app.models import ChatMessage, ChatMessageCreateDTO, ChatSession, ChatSessionCreateDTO, SearchHistory, SearchSession, SearchSessionCreateDTO, User, UserCreateDTO, UserCreateSignupDTO, UserUpdateDTO, UserUpdateSelfDTO
from sqlmodel import Session, select

# Dummy hash to use for timing attack prevention when user is not found
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

#=======================================================================================================
# USER METHODS
#=======================================================================================================

def get_or_create_google_user(
    session: Session,
    email: str,
    google_id: str,
    full_name: str | None
) -> User:
    """Get existing user or create new one from Google OAuth."""
    
    user = session.exec(
        select(User).where(User.google_id == google_id)
    ).first()
    
    if user:
        return user
    
    user = get_user_by_email(session=session, email=email)
    if user:
        
        user.google_id     = google_id
        user.auth_provider = AuthProvider.GOOGLE
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    
    user = User(
        email=email,
        full_name=full_name,
        google_id=google_id,
        auth_provider=AuthProvider.GOOGLE,
        is_active=True,
        hashed_password=""  # no password , user signs in using google account
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def create_user(*, session: Session, user_creation_data: UserCreateDTO | UserCreateSignupDTO) -> User:
    if isinstance(user_creation_data, UserCreateSignupDTO):
        resolved_subscription_tier = SubscriptionTier.FREE
    else:
        resolved_subscription_tier = (
            SubscriptionTier.PAID
            if user_creation_data.is_superuser
            else user_creation_data.subscription_tier
        )

    db_obj = User.model_validate(
        user_creation_data, 
        update={
            "hashed_password": get_password_hash(user_creation_data.password),
            "subscription_tier": resolved_subscription_tier,
}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_user(*, session:Session, user_update_data:UserUpdateDTO | UserUpdateSelfDTO, user:User) -> User:
    """
    CRUD method for user update.
    Called by superusers using UserUpdateDTO as a parameter.
    Called by regular users using UserUpdateSelfDTO as a parameter. 
    """
    user_data = user_update_data.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        extra_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    user.sqlmodel_update(user_data, update= extra_data)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(*, session:Session, email:str) -> User | None :
    """
    CRUD method for finding a user by their email.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

#=======================================================================================================
# SEARCH SESSION METHODS
#=======================================================================================================

def create_search_session(*, session:Session, owner_id:uuid.UUID, search_session_creation_data: SearchSessionCreateDTO) -> SearchSession:
    """
    CRUD method for search session creation.
    """
    db_obj = SearchSession.model_validate(
        search_session_creation_data, update={"owner_id": owner_id}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def update_search_session_status(*, session:Session, search_session: SearchSession, status: SearchSessionStatus, error_message: str | None) -> SearchSession:
    """
    CRUD method for search session update.
    """
    search_session.status = status
    search_session.error_message = error_message

    session.add(search_session)
    session.commit()
    session.refresh(search_session)

    return search_session

def get_search_session(*, session:Session, search_session_id:uuid.UUID) -> SearchSession :
    """
    CRUD method for finding search session using search session id.
    """
    return session.get(SearchSession, search_session_id)

#=======================================================================================================
# CHAT METHODS
#=======================================================================================================

def create_chat_session(*, session:Session, owner_id: uuid.UUID, chat_session_creation_data:ChatSessionCreateDTO) -> ChatSession:
    """
    CRUD method for chat session creation.
    """
    db_obj = ChatSession.model_validate(
        chat_session_creation_data,
        update={"owner_id":owner_id}
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def create_chat_message(*, session:Session, chat_creation_data:ChatMessageCreateDTO, role:ChatRole, chat_session_id:uuid.UUID) -> ChatMessage:
    """
    CRUD method for chat message creation.
    """
    db_obj = ChatMessage(
        content=chat_creation_data.content,
        role=role, 
        chat_session_id=chat_session_id
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def get_chat_sessions_by_user(*, session:Session, owner_id:uuid.UUID) -> list[ChatSession]:
    """
    CRUD method for finding chat sessions using the owner id.
    """
    statement = (
                select(ChatSession)
                .where(owner_id == owner_id)
                .order_by(ChatSession.created_at)
                )
    
    return session.exec(statement).all()

def get_chat_messages_by_session(*, session:Session, chat_session_id:uuid.UUID) -> list[ChatMessage]:
    """
    CRUD method for finding chat messages in a chat session.
    """
    statement = (
    select(ChatMessage)
    .where(ChatMessage.chat_session_id == chat_session_id)
    .order_by(ChatMessage.created_at)
)

    return session.exec(statement).all()

#=======================================================================================================
# SEARCH HISTORY METHOD
#=======================================================================================================

def create_search_history(*,
                        session:Session,
                        search_session_id:uuid.UUID,
                        step:AgentStep,
                        input:str,
                        output:str,
                        duration_ms:str) -> SearchHistory:
    """
    CRUD method for creating a search history.
    """
    db_obj = SearchHistory(search_session_id=search_session_id,
                           step=step,
                           input=input,
                           output=output,
                           duration_ms=duration_ms)
    
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

def authenticate(*, session: Session, email:str, password:str) -> User | None:
    """
    Method for authenticating the user.
    """
    user = get_user_by_email(session=session, email=email)
    if not user:
        # Prevent time attack
        verify_password(password, DUMMY_HASH)
        return None
    
    verified, updated_password_hash = verify_password(password, user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        user.hashed_password = updated_password_hash
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


    

    
