"""
agent/infrastructure/weather.py
--------------------------------
Provides weather summaries for destination and travel dates using Open-Meteo.
Automatically chooses forecast data for near-term dates and historical analogs
for long-range planning beyond forecast availability.

Endpoints used:
    GET /v1/search   → geocoding destination to latitude/longitude
    GET /v1/forecast → daily forecast (up to 16 days ahead)
    GET /v1/archive  → historical weather for long-range date analogs
"""

import logging
import requests
from datetime import date, timedelta
from langchain_core.tools import tool


logger = logging.getLogger(__name__)

GEOCODING_URL        = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_PARAMS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "weathercode"
]

WEATHER_CODE_DESCRIPTIONS = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2:  "Partly cloudy",
    3:  "Overcast",
    45: "Foggy",
    48: "Icy fog",
    51: "Light drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    80: "Slight showers",
    95: "Thunderstorm",
}


class WeatherService:
    """
    Provides weather retrieval and summarization using Open-Meteo APIs.
    Used by the Agent to inform itinerary quality and expectations.

    Search mode  → get_weather()      deterministic weather summary
    Chat mode    → get_weather_tool() ReAct tool wrapper for LLM calls
    Internal     → geocoding + source selection + normalization helpers
    """

    def __init__(
        self,
        geocoding_url: str = GEOCODING_URL,
        weather_forecast_url: str = WEATHER_FORECAST_URL,
        weather_historical_url: str = WEATHER_HISTORICAL_URL,
        daily_params: list[str] | None = None,
        request_timeout: int = 10,
    ) -> None:
        self.geocoding_url = geocoding_url
        self.weather_forecast_url = weather_forecast_url
        self.weather_historical_url = weather_historical_url
        self.daily_params = daily_params[:] if daily_params is not None else DAILY_PARAMS[:]
        self.request_timeout = request_timeout

    def get_weather(self, destination: str, date_from: str, date_to: str) -> dict | None:
        """
        Retrieve weather summary for a destination and date range.
        Selects forecast data for near-term dates, otherwise historical analog data.

        Args:
            destination: City or region name (e.g. 'Prague', 'Tokyo')
            date_from: Start date in ISO format (YYYY-MM-DD)
            date_to: End date in ISO format (YYYY-MM-DD)

        Returns:
            Weather summary dict with temperature, precipitation, and conditions,
            or None when geocoding/API retrieval fails.
        """
        coordinates = self.get_coordinates(destination)
        if not coordinates:
            logger.warning(f"Could not fetch coordinates for {destination}")
            return None

        if self.is_within_forecast_range(date_from):
            data = self._get_forecast(coordinates, date_from, date_to)
        else:
            data = self._get_historical(coordinates, date_from, date_to)

        if not data:
            logger.warning(f"Could not fetch weather data for {destination}")
            return None
        
        return self._build_summary(data, destination, coordinates)

    def get_coordinates(self, destination: str) -> dict | None:
        """
        Resolve destination coordinates with Open-Meteo geocoding.

        Args:
            destination: Destination string to geocode.

        Returns:
            Dict containing latitude, longitude, resolved place name, and country,
            or None when no match is found.
        """
        try:
            response = requests.get(
                self.geocoding_url,
                params={"name": destination, "count": 1},
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            data = response.json()

            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return {
                    "latitude":  result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "name":      result.get("name"),
                    "country":   result.get("country"),
                }

        except requests.RequestException as e:
            logger.error(f"Geocoding error for {destination}: {e}")

        return None

    def is_within_forecast_range(self, date_from: str) -> bool:
        """
        Check whether a date is within forecast API availability.

        Args:
            date_from: Start date in ISO format (YYYY-MM-DD).

        Returns:
            True if the date is within 16 days from today; otherwise False.
        """
        today      = date.today()
        start_date = date.fromisoformat(date_from)
        return start_date <= today + timedelta(days=16)

    def _get_forecast(self, coordinates: dict, date_from: str, date_to: str) -> dict | None:
        """
        Fetch forecast weather data for a coordinate range.

        Args:
            coordinates: Dict containing latitude and longitude.
            date_from: Forecast start date (YYYY-MM-DD).
            date_to: Forecast end date (YYYY-MM-DD).

        Returns:
            Forecast API JSON payload as dict, or None on request failure.
        """
        try:
            response = requests.get(
                self.weather_forecast_url,
                params={
                    "latitude":         coordinates["latitude"],
                    "longitude":        coordinates["longitude"],
                    "daily":            ",".join(self.daily_params),
                    "start_date":       date_from,
                    "end_date":         date_to,
                    "temperature_unit": "celsius",
                    "timezone":         "auto",
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Forecast API error: {e}")
            return None

    def _get_historical(self, coordinates: dict, date_from: str, date_to: str) -> dict | None:
        """
        Fetch historical weather data for long-range planning.
        Dates are shifted one year back to provide a seasonal analog.

        Args:
            coordinates: Dict containing latitude and longitude.
            date_from: Original travel start date (YYYY-MM-DD).
            date_to: Original travel end date (YYYY-MM-DD).

        Returns:
            Historical API JSON payload as dict, or None on request failure.
        """
        try:
            # Shift dates back by 1 year for historical comparison
            start = date.fromisoformat(date_from).replace(
                year=date.fromisoformat(date_from).year - 1
            )
            end = date.fromisoformat(date_to).replace(
                year=date.fromisoformat(date_to).year - 1
            )

            response = requests.get(
                self.weather_historical_url,
                params={
                    "latitude":         coordinates["latitude"],
                    "longitude":        coordinates["longitude"],
                    "daily":            ",".join(self.daily_params),
                    "start_date":       start.isoformat(),
                    "end_date":         end.isoformat(),
                    "temperature_unit": "celsius",
                    "timezone":         "auto",
                },
                timeout=self.request_timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Historical API error: {e}")
            return None

    def _build_summary(self, data: dict, destination: str, coordinates: dict) -> dict:
        """
        Build a normalized weather summary for agent consumption.
        Computes averages and derives a primary weather description.

        Args:
            data: Raw forecast or archive API payload.
            destination: Original user-provided destination name.
            coordinates: Resolved geocoding dict.

        Returns:
            Dict with destination metadata, aggregate temperatures,
            precipitation total, weather description, and forecast flag.
        """
        daily = data.get("daily", {})

        temp_max_list  = daily.get("temperature_2m_max", [])
        temp_min_list  = daily.get("temperature_2m_min", [])
        precip_list    = daily.get("precipitation_sum", [])
        weathercodes   = daily.get("weathercode", [])

        # Compute averages
        avg_temp_max = round(sum(temp_max_list) / len(temp_max_list), 1) if temp_max_list else None
        avg_temp_min = round(sum(temp_min_list) / len(temp_min_list), 1) if temp_min_list else None
        total_precip = round(sum(precip_list), 1) if precip_list else None

        # Most common weather condition
        main_code    = max(set(weathercodes), key=weathercodes.count) if weathercodes else None
        description  = WEATHER_CODE_DESCRIPTIONS.get(main_code, "Variable conditions")

        return {
            "destination":   destination,
            "resolved_name": coordinates.get("name"),
            "country":       coordinates.get("country"),
            "avg_temp_max":  avg_temp_max,
            "avg_temp_min":  avg_temp_min,
            "total_precip_mm": total_precip,
            "description":   description,
            "is_forecast":   self.is_within_forecast_range(daily.get("time", [""])[0]),
        }

# ── LangChain tool wrappers — used by Chat mode ReAct agent ─────────────

@tool
def get_weather_tool(destination: str, date_from: str, date_to: str) -> dict:
    """
    Get weather forecast or historical data for a travel destination.
    Use this when the user asks about weather conditions for a specific destination and dates.

    Args:
        destination: City name (e.g. 'Prague', 'Tokyo')
        date_from: Start date in ISO format (YYYY-MM-DD)
        date_to: End date in ISO format (YYYY-MM-DD)

    Returns:
        Weather summary dict. Returns an empty dict when data is unavailable.
    """
    service = WeatherService()
    return service.get_weather(destination, date_from, date_to) or {}