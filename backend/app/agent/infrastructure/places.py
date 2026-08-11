"""
agent/infrastructure/places.py
-------------------------------
Provides place discovery and place details using Google Places API (New).
Supports destination-level search and deep place enrichment with photo URLs.

Endpoints used:
    POST /v1/places:searchText → search places by text query
    GET  /v1/places/{id}        → fetch rich place details
    GET  /v1/{photo}/media      → resolve photo URI for display
"""

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
    Provides place search and place details using Google Places API (New).
    Used by the Agent for destination planning and recommendations.

    Search mode  → get_places()         deterministic category search
    Chat mode    → get_places_tool()    ReAct tool for attractions/restaurants
    Chat mode    → get_place_details()  enriches one place with deep metadata
    """

    def __init__(self):
        config = get_agent_config()
        self.api_key = config.google_maps_api_key
        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type":   "application/json",
        }

    def get_places(self, destination: str, category: str) -> list[dict]:
        """
        Search for places in a destination by category.
        Uses Text Search (New) and returns normalized records.

        Args:
            destination: City or region name (e.g. 'Prague', 'Tokyo')
            category: Place category such as 'attractions' or 'restaurants'

        Returns:
            List of place dicts including ID, rating, address, types, and one photo URL.
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
        Fetch detailed information for a specific place.
        Used when the user asks for deeper context about a selected place.

        Args:
            place_id: Google Places ID for the target place.

        Returns:
            Dict with ratings, opening hours, editorial summary, reviews,
            accessibility metadata, and up to 3 photo URLs.
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
        Resolve a direct photo URL from a Google Places photo resource name.
        Uses skipHttpRedirect=true so the API returns photoUri directly.

        Args:
            photo_name: API photo resource name from a place payload.

        Returns:
            Direct photo URI if available; otherwise None.
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
        Parse raw Text Search place records into normalized dicts.
        Enriches each place with one resolved photo URL when available.

        Args:
            places: Raw list from Text Search API response.

        Returns:
            List of normalized place dicts used by the agent response layer.
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
        Parse a raw Place Details payload into a normalized details dict.
        Resolves up to 3 photo URLs for richer UI rendering.

        Args:
            data: Raw Place Details API response payload.

        Returns:
            Normalized place details dict with metadata and resolved photo URLs.
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

    Returns:
        List of normalized places for the requested destination and category.
    """
    return PlacesService().get_places(destination, category)


@tool
def get_place_details_tool(place_id: str) -> dict:
    """
    Get detailed information about a specific place.
    Use this when the user asks for more details about a specific place.

    Args:
        place_id: Google Places ID (e.g. 'ChIJN1t_tDeuEmsRUsoyG83frY4')

    Returns:
        Detailed place dict with hours, reviews, summary, and photo URLs.
    """
    return PlacesService().get_place_details(place_id)