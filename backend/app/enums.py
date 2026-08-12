from enum import StrEnum

class ChatRole(StrEnum):
    """
    Enum representing the role of a participant in a chat session.
    """
    USER = "user"
    ASSISTANT = "assistant"

class SearchSessionStatus(StrEnum):
    """
    Enum representing the status of a search session.
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentStep(StrEnum):
    """
    Enum representing the steps of the AI travel agent's process.
    """
    RAG_RETRIEVAL  = "rag_retrieval"
    WEATHER_FETCH  = "weather_fetch"
    PLACES_FETCH   = "places_fetch"
    FLIGHTS_FETCH  = "flights_fetch"   
    LLM_GENERATION = "llm_generation"

class TravelPackageTier(StrEnum):
    """
    Enum representing the tiers of travel packages.
    """
    BUDGET = "budget"
    STANDARD = "standard"
    LUXURY = "luxury"

class Currency(StrEnum):
    """
    Enum representing currency codes for exchange rate differences.
    """
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"

class PartOfDay(StrEnum):
    """
    Enum representing parts of one day.
    """
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class ActivityType(StrEnum):
    """
    Enum representing the different kinds of activities.
    """
    SIGHTSEEING = "sightseeing"
    FOOD = "food"
    ADVENTURE = "adventure"

class AccommodationType(StrEnum):
    """
    Enum representing the type of an accommodation.
    """
    HOTEL = "hotel"
    HOSTEL = "hostel"
    AIRBNB = "airbnb"

class SubscriptionTier(StrEnum):
    """
    Enum representing the subscription tiers for users.
    """
    FREE = "free"
    PAID = "paid"

class AuthProvider(StrEnum):
    """
    Enum representing the authentication providers for users.
    """
    GOOGLE = "google"
    EMAIL = "email"

class TripType(StrEnum):
    SOLO     = "solo"
    FAMILY   = "family"
    ROMANTIC = "romantic"
    FRIENDS  = "friends"

