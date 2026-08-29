"""Tests for weather service."""

from unittest.mock import patch, MagicMock
from app.agent.infrastructure.weather import WeatherService


class TestWeatherService:

    @patch("app.agent.infrastructure.weather.requests.get")
    def test_returns_weather_data(self, mock_get):
        # First call: geocoding; second call: forecast
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {
                "results": [{"latitude": 50.08, "longitude": 14.42, "name": "Prague", "country": "Czechia"}]
            }),
            MagicMock(status_code=200, json=lambda: {
                "daily": {
                    "time": ["2026-09-01", "2026-09-02", "2026-09-03"],
                    "temperature_2m_max": [20, 22, 21],
                    "temperature_2m_min": [10, 12, 11],
                    "precipitation_sum": [0, 1, 0],
                    "weathercode": [0, 61, 0],
                }
            }),
        ]

        svc = WeatherService()
        result = svc.get_weather("Prague", "2026-09-01", "2026-09-04")
        assert result is not None
        assert isinstance(result, dict)

    @patch("app.agent.infrastructure.weather.requests.get")
    def test_bad_geocoding_returns_none(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {})

        svc = WeatherService()
        result = svc.get_weather("Nowhereland", "2026-09-01", "2026-09-04")
        assert result is None

    def test_forecast_range_check(self):
        svc = WeatherService()
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        far_future = (date.today() + timedelta(days=100)).isoformat()
        assert svc.is_within_forecast_range(tomorrow) is True
        assert svc.is_within_forecast_range(far_future) is False
