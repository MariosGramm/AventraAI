import uuid
from app.enums import AccommodationType, ActivityType, AgentStep, ChatRole, Currency, PartOfDay, SearchSessionStatus, TravelPackageTier
from sqlmodel import ARRAY, Column, DateTime, Relationship, SQLModel, Field, String
from pydantic import EmailStr
from datetime import datetime, UTC

# Shared Models
class UserBase(SQLModel):
    """
    Base model for user-related data.
    """ 
    first_name: str = Field(max_length=50, description="The first name of the user.")
    last_name: str = Field(max_length=50, description="The last name of the user.")
    email : EmailStr = Field(max_length=100, description="The email address of the user.")
    is_active: bool = Field(default=True, description="Indicates whether the user is active.")
    is_superuser: bool = Field(default=False, description="Indicates whether the user has superuser privileges.")

class AuditableBase(SQLModel):
    """
    Base model for auditable entities.
    """
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # type: ignore
    )

#=======================================================================================================
# USER MODELS
#=======================================================================================================

# User creation DTOs
class UserCreateDTO(UserBase):
    """
    Model for creating a new user.
    Used ONLY by the superuser to create a new user.
    Inherits from UserBase and adds a password field.
    """
    password: str = Field(min_length=8, description="The password for the user account.")

class UserCreateSignupDTO(SQLModel):
    """
    Used by the user to sign up.
    Model for user signup.
    """
    first_name: str = Field(max_length=50, description="The first name of the user.")
    last_name: str = Field(max_length=50, description="The last name of the user.")
    email : EmailStr = Field(max_length=100, description="The email address of the user.")
    password: str = Field(min_length=8, description="The password for the user account.")
    
# User update DTOs
class UserUpdateDTO(SQLModel):
    """
    Model for updating user information.
    Used ONLY by the superuser to update user information.
    All fields are optional to allow partial updates.
    """
    email: EmailStr | None = Field(default=None, max_length=100, description="The email address of the user.")
    first_name: str | None = Field(default=None, max_length=50, description="The first name of the user.")
    last_name: str | None = Field(default=None, max_length=50, description="The last name of the user.")
    password: str | None = Field(default=None, min_length=8, description="The password for the user account.")
    is_active: bool | None = Field(default=None, description="Indicates whether the user is active.")
    is_superuser: bool | None = Field(default=None, description="Indicates whether the user has superuser privileges.")


class UserUpdateSelfDTO(SQLModel):
    """
    Model for updating user information by the user themselves.
    All fields are optional to allow partial updates.
    """
    first_name: str | None = Field(default=None, max_length=50, description="The first name of the user.")
    last_name: str | None = Field(default=None, max_length=50, description="The last name of the user.")
    password: str | None = Field(default=None, min_length=8, description="The password for the user account.")
    email: EmailStr | None = Field(default=None, max_length=100, description="The email address of the user.")

class UserUpdatePasswordDTO(SQLModel):
    """
    Model for updating user password.
    All fields are required to ensure proper password update.
    """
    current_password: str = Field(min_length=8, description="The current password of the user.")
    new_password: str = Field(min_length=8, description="The new password for the user account.")

# User entity model
class User(UserBase, AuditableBase, table=True):
    __tablename__ = "user"

    """
    Database entity for the User.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the user.")
    hashed_password: str = Field(max_length=255, description="The hashed password for the user account.")

    chat_sessions: list["ChatSession"] = Relationship(back_populates="owner", cascade_delete=True)
    search_sessions: list["SearchSession"] = Relationship(back_populates="owner", cascade_delete=True)
    
# Public user DTOs for API responses
class UserPublicDTO(UserBase):
    """
    Public representation of the User model.
    Used for API responses to avoid exposing sensitive information.
    """
    id: uuid.UUID = Field(description="The unique identifier for the user.")
    created_at: datetime | None = Field(description="The timestamp when the user was created.")

class UsersPublicDTO(SQLModel):
    """
    Model for a list of public user representations.
    Used for API responses when returning multiple users.
    """
    users: list[UserPublicDTO] = Field(description="A list of public user representations.")
    count: int = Field(description="The total number of users returned.")

#=======================================================================================================
# CHAT MODELS
#=======================================================================================================

# Chat session entity model 
class ChatSession(AuditableBase, table=True):
    __tablename__ = "chat_session"

    """
    Database entity for the ChatSession.
    Represents a chat session between a user and the AI travel agent.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the chat session.")
    owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE", description="The unique identifier of the user associated with this chat session.")
    title: str | None = Field(default=None, max_length=100, description="The title of the chat session")
    owner: "User" = Relationship(back_populates="chat_sessions")
    messages : list["ChatMessage"] = Relationship(back_populates="session", cascade_delete=True)

# Public chat session DTOs for API responses
class ChatSessionPublicDTO(SQLModel):
    """
    Public representation of the ChatSession model.
    Used for API responses to avoid exposing sensitive information.
    """
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str | None
    created_at: datetime | None
    updated_at: datetime | None

class ChatSessionsPublicDTO(SQLModel):
    """
    Model for a list of public chat session representations.
    Used for API responses when returning multiple chat sessions.
    """    
    chat_sessions: list[ChatSessionPublicDTO] = Field(description="A list of public chat session representations.")
    count: int = Field(description="The total number of chat sessions returned.")

# Create DTO for ChatSession creation
class ChatSessionCreateDTO(SQLModel):
    title: str | None = Field(
        default=None,
        max_length=100,
        description="Optional title. Auto-generated if not provided."
    )

# Chat message entity model
class ChatMessage(AuditableBase, table=True):
    __tablename__ = "chat_message"

    """
    Database entity for the ChatMessage.
    Represents a single message in a chat session.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the chat message.")
    chat_session_id: uuid.UUID = Field(foreign_key="chat_session.id", ondelete="CASCADE", description="The unique identifier of the chat session associated with this message.")
    role : ChatRole = Field(description="The role of the participant who sent the message (user or assistant).")    
    content: str = Field(description="The content of the chat message.")
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    session: "ChatSession" = Relationship(back_populates="messages")

# Public chat message DTOs for API responses
class ChatMessagePublicDTO(SQLModel):
    """
    Public representation of the ChatMessage model.
    Used for API responses to avoid exposing sensitive information.
    """
    role: ChatRole
    content: str
    created_at: datetime | None


class ChatMessagesPublicDTO(SQLModel):
    """
    Model for a list of public chat message representations.
    Used for API responses when returning multiple chat messages.
    """ 
    data: list[ChatMessagePublicDTO]
    count: int

# Create DTO for ChatMessage creation
class ChatMessageCreateDTO(SQLModel):
    content: str = Field(
        description="The message content sent by the user."
    )

#Response DTO for Chat response
class ChatResponseDTO(SQLModel):
    session_id: uuid.UUID    
    role: ChatRole           
    content: str             
    created_at: datetime | None

#=======================================================================================================
# SEARCH MODELS
#=======================================================================================================

# Search session entity model
class SearchSession(AuditableBase, table=True):
    __tablename__ = "search_session"

    """
    Database entity for the SearchSession.
    Represents a search session initiated by a user.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the search session.")
    owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE", description="The unique identifier of the user associated with this search session.")
    destination: str = Field(max_length=200, description="The travel destination for the search session.")
    date_from: datetime = Field(description="The start date for the travel search.")
    date_to: datetime = Field(description="The end date for the travel search.")
    budget: float | None = Field(default=None, description="The budget for the travel search.")
    currency: Currency = Field(default=Currency.EUR, description="The currency code for the budget (e.g., USD, EUR).")
    status: SearchSessionStatus = Field(default=SearchSessionStatus.PENDING, description="The status of the search session (pending, completed, or failed).")
    error_message: str | None = Field(default=None, description="An optional error message if the search session failed.")

    owner: "User" = Relationship(back_populates="search_sessions")
    search_history: list["SearchHistory"] = Relationship(back_populates="search_session", cascade_delete=True)
    travel_packages: list["TravelPackage"] = Relationship(back_populates="search_session", cascade_delete=True)

# Public search session DTO for API responses
class SearchSessionPublicDTO(SQLModel):
    """
    Public representation of the SearchSession model.
    Used for API responses to avoid exposing sensitive information.
    """
    id: uuid.UUID
    status: SearchSessionStatus
    destination: str
    date_from: datetime
    date_to: datetime
    budget: float | None
    currency: Currency
    created_at: datetime | None
    packages: list["TravelPackagePublicDTO"]

class SearchSessionsPublicDTO(SQLModel):
    """
    Model for a list of public search session representations.
    Used for API responses when returning multiple search sessions.
    """
    data: list[SearchSessionPublicDTO]
    count: int

# Create DTO for SearchSession creation
class SearchSessionCreateDTO(SQLModel):
    destination: str = Field(
        max_length=200,
        description="The travel destination."
    )
    date_from: datetime = Field(
        description="The start date of the trip."
    )
    date_to: datetime = Field(
        description="The end date of the trip."
    )
    budget: float | None = Field(
        default=None,
        description="Optional budget for the trip."
    )
    currency: Currency = Field(
        default=Currency.EUR,
        description="The currency of the budget."
    )

# Search history entity model
class SearchHistory(SQLModel, table=True):
    __tablename__ = "search_history"

    """
    Database entity for the SearchHistory.
    Represents a record of a completed search session.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the search history record.")
    search_session_id: uuid.UUID = Field(foreign_key="search_session.id", ondelete="CASCADE", description="The unique identifier of the search session associated with this history record.")
    step: AgentStep = Field(description="The step of the AI travel agent's process that this history record corresponds to.")
    input: str = Field(description="The input data for the corresponding step of the AI travel agent's process.")          
    output: str = Field(description="The output data for the corresponding step of the AI travel agent's process.")        
    duration_ms: float = Field(description="The duration in milliseconds for the corresponding step of the AI travel agent's process.")
    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    search_session: "SearchSession" = Relationship(back_populates="search_history")

#=======================================================================================================
# TRAVEL MODELS (Search results)
#=======================================================================================================

# Travel package entity model
class TravelPackage(SQLModel, table=True):
    __tablename__ = "travel_package"

    """
    Database entity for the TravelPackage.
    Represents a travel package as a search result.
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the travel package.")
    session_id: uuid.UUID = Field(foreign_key="search_session.id", description="The unique identifier of the search session associated with this travel package.")

    tier : TravelPackageTier = Field(description="The tier of the travel package (budget, standard, or luxury).")
    estimated_cost_min: float = Field(description="The minimum estimated cost of the travel package")
    estimated_cost_max: float = Field(description="The maximum estimated cost of the travel package")
    currency: Currency = Field(default=Currency.EUR, description="The currency code for the budget (e.g., USD, EUR).")

    transportation: str | None = Field(default= None, description= "The description of the tranportation")
    travel_tips: list[str] | None = Field(default_factory=list, sa_column=Column(ARRAY(String)), description="Extra information for the visitors in the form of tips")

    # Weather summary might be unavailable if the travel date is outside the available forecast range.
    weather_summary: str | None = Field(default=None, description="Weather summary for the period which the visitors will visit the place")

    created_at: datetime | None = Field(
        default_factory= lambda: datetime.now(UTC), 
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    search_session : SearchSession = Relationship(back_populates="travel_packages")
    itinerary: list["Itinerary"] = Relationship(back_populates="package", cascade_delete=True)
    accommodations: list["Accommodation"] = Relationship(back_populates="package", cascade_delete=True)

# Public travel package DTO for API responses
class TravelPackagePublicDTO(SQLModel):
    id: uuid.UUID
    tier: TravelPackageTier
    estimated_cost_min: float
    estimated_cost_max: float
    currency: Currency
    transportation: str | None
    travel_tips: list[str] | None
    weather_summary: str | None
    itinerary: list["ItineraryPublicDTO"]
    accommodations: list["AccommodationPublicDTO"]

# Itinerary package entity model
class Itinerary(SQLModel, table=True):
    __tablename__ = "itinerary"

    """
    Database entity for the Itinerary.
    Represents an itinerary (a DAILY plan) which consists of activities.
    One record = One day
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the itinerary.")
    travel_package_id: uuid.UUID = Field(foreign_key="travel_package.id", ondelete="CASCADE")

    day_number:int = Field(description="The number of the day of the itinerary")
    date: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    description: str = Field(description="The description of the day's itinerary")
    estimated_daily_cost: float | None = Field(default=None)

    package: TravelPackage = Relationship(back_populates="itinerary")
    activities: list["Activity"] = Relationship(back_populates="itinerary", cascade_delete=True)

# Public itinerary DTO for API responses
class ItineraryPublicDTO(SQLModel):
    id: uuid.UUID
    day_number: int
    date: datetime | None
    description: str
    estimated_daily_cost: float | None
    activities: list["ActivityPublicDTO"]

# Activity entity model
class Activity(SQLModel, table=True):
    __tablename__ = "activity"

    """
    Database entity for the Activity.
    Represents an activity that the visitor can take part in.
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the activity.")
    type: ActivityType = Field(default=ActivityType.SIGHTSEEING, description="The type of the activity (sightseeing, adventure or food)")
    itinerary_id: uuid.UUID = Field(foreign_key="itinerary.id", ondelete="CASCADE")
    title: str = Field(max_length=200)
    estimated_cost: float | None = Field(default=None, description="The estimated cost of the activity")
    average_duration_hours: int | None = Field(default=None, description="The average duration of the activity in hours")
    part_of_day: PartOfDay = Field(default=PartOfDay.MORNING, description="The part of the day the activity (morning, afternoon, evening)")

    itinerary: Itinerary = Relationship(back_populates="activities")

#Public activity DTO for API responses
class ActivityPublicDTO(SQLModel):
    id: uuid.UUID
    type: ActivityType
    title: str
    estimated_cost: float | None
    average_duration_hours: int | None
    part_of_day: PartOfDay


# Accommodation entity model
class Accommodation(SQLModel, table = True):
    __tablename__ = "accommodation"

    """
    Database entity for the Accommodation.
    Represents an accommodation a visitor can stay. 
    """
    id : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="The unique identifier for the accommodation.")
    package_id: uuid.UUID = Field(foreign_key="travel_package.id", ondelete="CASCADE")
    name:str = Field(max_length=200, description="The name of the accommodation")
    type: AccommodationType = Field(default=AccommodationType.HOTEL, description="The type of the accommodation (hotel or hostel or airbnb).")
    area: str | None = Field(default=None, max_length=100, description="The area in which the accommodation is located at.")
    cost_per_night: float | None = Field(default=None)
    rating: float | None = Field(default=None, description="The rating of the accommodation. Rated from 1.0 to 5.0")
    extra_info: str | None = Field(default=None, description="Any extra information regarding the accommodation")

    package: TravelPackage = Relationship(back_populates="accommodations")

# Public accommodation DTO for API responses
class AccommodationPublicDTO(SQLModel):
    id: uuid.UUID
    name: str
    type: AccommodationType
    area: str | None
    cost_per_night: float | None
    rating: float | None
    extra_info: str | None

# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

# API schema: payload used for changing an existing password.
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
