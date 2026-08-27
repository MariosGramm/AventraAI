"""
agent/infrastructure/hotels.py
--------------------------------
Provides real-time hotel search and pricing using StayingAPI.
Supports both deterministic (Search mode) and ReAct (Chat mode) workflows.

Endpoints used:
  GET /v1/search        → hotel discovery by location + dates
  GET /v1/price-compare → cross-OTA price comparison for a known property
  GET /v1/reviews       → normalized reviews for a listing
"""

import logging
import requests
from ..config import get_agent_config

logger = logging.getLogger(__name__)


class HotelsService:
    """
    Provides hotel search, pricing, and reviews using StayingAPI.
    Used by the Agent for travel planning.

    Search mode  → get_hotels()       deterministic, called by graph.py
    Chat mode    → get_hotels_tool()  ReAct tool, called by LLM agent
    """

    BASE_URL = "https://api.stayingapi.com/v1"

    # Platforms to search across
    DEFAULT_PLATFORMS = "booking,google"

    def __init__(self):
        config = get_agent_config()
        self.api_key = config.stayingapi_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }


    def get_hotels(
        self,
        destination:  str,
        check_in:     str,
        check_out:    str,
        adults:       int = 2,
        limit:        int = 5,
        currency:     str = "EUR",
    ) -> list[dict]:
        """
        Search for hotels in a destination with real-time pricing.
        Used in Search mode (deterministic).

        Args:
            destination: City name and country (e.g. 'Prague, CZ')
            check_in:    ISO date string (YYYY-MM-DD)
            check_out:   ISO date string (YYYY-MM-DD)
            adults:      Number of adults (default 2)
            limit:       Maximum number of results (default 5)
            currency:    Currency code (default EUR)

        Returns:
            List of hotel dicts with name, rating, price, and booking URLs.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={
                    "location":  destination,
                    "checkIn":   check_in,
                    "checkOut":  check_out,
                    "adults":    adults,
                    "platforms": self.DEFAULT_PLATFORMS,
                    "limit":     limit,
                    "currency":  currency,
                },
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
            hotels = response.json().get("data", [])
            parsed = [self._parse_hotel(h, currency) for h in hotels]
            dest_lower = destination.lower()
            filtered = [h for h in parsed if self._is_relevant(h, dest_lower)]
            return filtered

        except requests.RequestException as e:
            logger.error(f"Hotel search error for {destination}: {e}")
            return []

    def get_price_compare(
        self,
        hotel_name:  str,
        location:    str,
        check_in:    str,
        check_out:   str,
        adults:      int = 2,
        currency:    str = "EUR",
    ) -> dict | None:
        """
        Get cross-OTA price comparison for a specific hotel.
        Returns the cheapest option with booking URLs for each OTA.

        Args:
            hotel_name: Exact hotel name (e.g. 'Hotel Aria Prague')
            location:   City and country (e.g. 'Prague, CZ')
            check_in:   ISO date string (YYYY-MM-DD)
            check_out:  ISO date string (YYYY-MM-DD)
            adults:     Number of adults (default 2)
            currency:   Currency code (default EUR)

        Returns:
            Dict with min price, median price, and offers per OTA.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/price-compare",
                params={
                    "name":     hotel_name,
                    "location": location,
                    "checkIn":  check_in,
                    "checkOut": check_out,
                    "adults":   adults,
                    "currency": currency,
                },
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            return self._parse_price_compare(data)

        except requests.RequestException as e:
            logger.error(f"Price compare error for {hotel_name}: {e}")
            return None

    def get_reviews(
        self,
        listing_id: str,
        platform:   str = "booking",
        limit:      int = 5,
    ) -> dict | None:
        """
        Fetch normalized reviews for a hotel listing.

        Args:
            listing_id: Platform-specific listing ID
            platform:   OTA platform (e.g. 'booking', 'airbnb')
            limit:      Number of reviews to return (default 5)

        Returns:
            Dict with rating summary and sample reviews.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/reviews",
                params={
                    "listingId": listing_id,
                    "platform":  platform,
                    "limit":     limit,
                },
                headers=self.headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            return self._parse_reviews(data)

        except requests.RequestException as e:
            logger.error(f"Reviews error for listing {listing_id}: {e}")
            return None


    def _is_relevant(self, hotel: dict, destination_lower: str) -> bool:
        """Check if hotel location matches the requested destination."""
        loc = hotel.get("location", {})
        city = (loc.get("city") or "").lower()
        address = (loc.get("address") or "").lower()
        name = (hotel.get("name") or "").lower()
        dest_parts = destination_lower.split(",")[0].split()
        return any(part in city or part in address or part in name for part in dest_parts)

    def _parse_hotel(self, hotel: dict, currency: str) -> dict:
        """Parse a single hotel from /v1/search response."""
        platform   = hotel.get("platform")
        listing_id = hotel.get("id")

        # Extract price info
        price_data  = hotel.get("price") or {}
        price_total = price_data.get("total")
        price_night = price_data.get("perNight")

        # Extract rating
        rating       = hotel.get("rating")
        rating_scale = hotel.get("ratingScale")  # Airbnb=5, Booking=10

        # Extract location
        location = hotel.get("location", {})

        return {
            "id":           listing_id,
            "platform":     platform,
            "name":         hotel.get("name"),
            "type":         hotel.get("propertyType"),
            "rating":       rating,
            "rating_scale": rating_scale,
            "review_count": hotel.get("reviewCount"),
            "amenities":    hotel.get("amenities", []),
            "location": {
                "address": location.get("address"),
                "city":    location.get("city"),
                "lat":     location.get("lat"),
                "lng":     location.get("lng"),
            },
            "price": {
                "per_night": price_night,
                "total":     price_total,
                "currency":  currency,
            },
            "booking_url": self._build_booking_url(platform, listing_id),
            "thumbnail":   hotel.get("thumbnail"),
        }

    def _parse_price_compare(self, data: dict) -> dict:
        """Parse /v1/price-compare response into clean dict."""
        offers = []
        for offer in data.get("offers", []):
            offers.append({
                "ota":         offer.get("ota"),
                "total_price": offer.get("totalPrice"),
                "currency":    offer.get("currency"),
                "url":         offer.get("url"),  # ← direct booking URL from API
            })

        return {
            "property":  data.get("property"),
            "check_in":  data.get("checkIn"),
            "check_out": data.get("checkOut"),
            "currency":  data.get("currency"),
            "min_price": data.get("min"),      # cheapest OTA
            "median":    data.get("median"),   # median price
            "offers":    offers,               # per-OTA prices + URLs
        }

    def _parse_reviews(self, data: dict) -> dict:
        """Parse reviews response into clean dict."""
        reviews = []
        for review in data.get("reviews", []):
            reviews.append({
                "rating":        review.get("rating"),
                "traveler_type": review.get("travelerType"),
                "text":          review.get("text"),
                "date":          review.get("stayDate"),
            })

        return {
            "overall_rating": data.get("summary", {}).get("rating"),
            "review_count":   data.get("summary", {}).get("reviewsCount"),
            "reviews":        reviews,
        }

    def _build_booking_url(self, platform: str | None, listing_id: str | None) -> str | None:
        """
        Build a direct booking URL from platform name and listing ID.
        Used as fallback — /v1/price-compare returns actual URLs per OTA.
        """
        if not platform or not listing_id:
            return None

        templates = {
            "booking":       f"https://www.booking.com/hotel/{listing_id}.html",
            "airbnb":        f"https://www.airbnb.com/rooms/{listing_id}",
            "vrbo":          f"https://www.vrbo.com/{listing_id}",
            "google_hotels": f"https://hotels.google.com/entity/{listing_id}",
        }
        return templates.get(platform)
