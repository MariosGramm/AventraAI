import requests
import logging
from langchain_core.tools import tool
from ..config import get_agent_config

logger = logging.getLogger(__name__)

# Level 1 — Search 
SEARCH_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.rating,"
    "places.formattedAddress,"
    "places.priceLevel,"
    "places.types,"
    "places.photos"  # ← for photo names
)

# Level 2 — Details
DETAILS_FIELD_MASK = (
    "id,"
    "displayName,"
    "rating,"
    "formattedAddress,"
    "regularOpeningHours,"
    "priceLevel,"
    "reviews,"
    "photos,"          # ← for photo names
    "editorialSummary,"
    "accessibilityOptions"
)

TEXT_SEARCH_URL  = "https://places.googleapis.com/v1/places:searchText"
PLACE_DETAIL_URL = "https://places.googleapis.com/v1/places"
PLACE_PHOTOS_URL = "https://places.googleapis.com/v1"


class PlacesService:
    """
    Provides methods to interact with the Google Places API (New).
    Used by the Agent for travel planning — attractions and restaurants.
    """

    def __init__(self):
        config = get_agent_config()
        self.api_key = config.google_places_api_key
        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type":   "application/json",
        }

    def get_places(self, destination: str, category: str) -> list[dict]:
        """
        Search for places in a destination by category.
        Uses Text Search (New) API.
        Returns clean list with one photo_url per place.
        """
        queries = {
            "attractions": f"top tourist attractions in {destination}",
            "restaurants": f"best restaurants in {destination}",
        }
        query = queries.get(category, f"{category} in {destination}")

        headers = {**self.headers, "X-Goog-FieldMask": SEARCH_FIELD_MASK}

        response = requests.post(
            TEXT_SEARCH_URL,
            json={"textQuery": query, "maxResultCount": 10, "languageCode": "en"},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            places = response.json().get("places", [])
            return self._parse_places(places)
        else:
            logger.error(f"Places search error: {response.status_code} — {response.text}")
            return []

    def get_place_details(self, place_id: str) -> dict:
        """
        Fetch detailed information about a specific place.
        Used in chat mode when user asks for more details.
        Returns full details with up to 3 photo URLs.
        """
        headers = {**self.headers, "X-Goog-FieldMask": DETAILS_FIELD_MASK}

        response = requests.get(
            f"{PLACE_DETAIL_URL}/{place_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return self._parse_place_details(data)
        else:
            logger.error(f"Place details error: {response.status_code} — {response.text}")
            return {}

    def _get_photo_url(self, photo_name: str) -> str | None:
        """
        Fetch a live photo URL using Place Photos (New) API.
        Uses skipHttpRedirect=true to get the photoUri directly.
        Called by _parse_places() and _parse_place_details().
        """
        try:
            response = requests.get(
                f"{PLACE_PHOTOS_URL}/{photo_name}/media",
                params={
                    "maxWidthPx":       800,
                    "skipHttpRedirect": "true",
                    "key":              self.api_key
                },
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("photoUri")
        except requests.RequestException as e:
            logger.error(f"Photo fetch error: {e}")
        return None

    def _parse_places(self, places: list) -> list[dict]:
        """
        Parse raw Text Search response into clean dicts.
        Fetches one photo URL per place.
        """
        results = []
        for place in places:
            # Get first photo URL if available
            photo_url = None
            photos = place.get("photos", [])
            if photos:
                photo_url = self._get_photo_url(photos[0].get("name"))

            results.append({
                "id":          place.get("id"),
                "name":        place.get("displayName", {}).get("text"),
                "rating":      place.get("rating"),
                "address":     place.get("formattedAddress"),
                "price_level": place.get("priceLevel"),
                "types":       place.get("types", []),
                "photo_url":   photo_url,   
            })
        return results

    def _parse_place_details(self, data: dict) -> dict:
        """
        Parse raw Place Details response into clean dict.
        Fetches up to 3 photo URLs.
        """
        # Get up to 3 photo URLs
        photo_urls = []
        for photo in data.get("photos", [])[:3]:
            url = self._get_photo_url(photo.get("name"))
            if url:
                photo_urls.append(url)

        return {
            "id":            data.get("id"),
            "name":          data.get("displayName", {}).get("text"),
            "rating":        data.get("rating"),
            "address":       data.get("formattedAddress"),
            "price_level":   data.get("priceLevel"),
            "opening_hours": data.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
            "editorial":     data.get("editorialSummary", {}).get("text"),
            "reviews":       data.get("reviews", []),
            "photo_urls":    photo_urls,  # ← up to 3 photo URLs
            "accessibility": data.get("accessibilityOptions", {}),
        }


# ── LangChain tool wrappers — used by Chat mode ReAct agent ─────────────

@tool
def get_places_tool(destination: str, category: str) -> list[dict]:
    """
    Search for places in a destination.
    Use this when the user asks about attractions or restaurants.
    Args:
        destination: City name (e.g. 'Prague', 'Tokyo')
        category: 'attractions' or 'restaurants'
    """
    return PlacesService().get_places(destination, category)


@tool
def get_place_details_tool(place_id: str) -> dict:
    """
    Get detailed information about a specific place.
    Use this when the user asks for more details about a specific place.
    Args:
        place_id: Google Places ID (e.g. 'ChIJN1t_tDeuEmsRUsoyG83frY4')
    """
    return PlacesService().get_place_details(place_id)