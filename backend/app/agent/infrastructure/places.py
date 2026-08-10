from backend.app.agent.config import get_config
import requests
import logging

logger = logging.getLogger(__name__)
GOOGLE_MAPS_API_KEY = get_config().google_maps_api_key

PLACES_URL = f"https://places.googleapis.com/v1/places/GyuEmsRBfy61i59si0?fields=addressComponents&key={GOOGLE_MAPS_API_KEY}"

class PlacesService:
    """
    PlacesService provides methods to interact with the Google Places API.
    Used by the Agent as a tool to fetch real-time data for travel planning.
    Service involves deterministic workflows as well as ReAct workflows.
    """

    def __init__(self, places_api_key: str = GOOGLE_MAPS_API_KEY, places_url: str = PLACES_URL) -> None:
        self.places_api_key = places_api_key
        self.places_url = places_url



