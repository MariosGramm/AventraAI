
from datetime import date


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
FLIGHTS_URL = "https://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/US/USD/en-US" #change?
HOTELS_URL = "https://api.stayingapi.com/v1"
DAILY_PARAMS = [
    "temperature_2m_max",    # maximum daily temperature (°C)
    "temperature_2m_min",    # minimum daily temperature (°C)
    "precipitation_sum",     # total daily precipitation (mm)
    "weathercode"            # weather code (0=clear, 3=cloudy etc.)
]



class WeatherService:
    """
    WeatherService provides methods to interact with weather, flight, places and hotels APIs.
    Used by the Agent as a tool to fetch real-time data for travel planning.
    Service involves deterministic workflows as well as ReAct workflows.
    """

    def __init__(self,
                GEOCODING_URL=GEOCODING_URL,
                WEATHER_FORECAST_URL=WEATHER_FORECAST_URL,
                WEATHER_HISTORICAL_URL=WEATHER_HISTORICAL_URL,
                FLIGHTS_URL=FLIGHTS_URL,
                HOTELS_URL=HOTELS_URL,
                DAILY_PARAMS=DAILY_PARAMS
                ):
        self.geocoding_url = GEOCODING_URL
        self.weather_forecast_url = WEATHER_FORECAST_URL
        self.weather_historical_url = WEATHER_HISTORICAL_URL
        self.flights_url = FLIGHTS_URL
        self.hotels_url = HOTELS_URL
        self.daily_params = DAILY_PARAMS

    def get_weather(self, destination, date_from, date_to) -> dict:
        """
        Fetches weather data for the given destination and date range.
        Returns a summary of the weather conditions.
        """
        # Implementation to fetch weather data from the APIs
        pass

    def get_coordinates(self, destination) -> dict | None:
        """
        Fetches geographical coordinates (latitude and longitude) for the given destination.
        Returns a dictionary with 'latitude' and 'longitude'.
        """
        

    



