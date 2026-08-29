"""Tests for the airport code resolver."""

from app.agent.infrastructure.airport_codes import resolve_city_iata


class TestAirportCodes:

    def test_major_city_override(self):
        assert resolve_city_iata("Paris") == "CDG"
        assert resolve_city_iata("London") == "LHR"

    def test_case_insensitive(self):
        assert resolve_city_iata("paris") == "CDG"
        assert resolve_city_iata("LONDON") == "LHR"

    def test_known_city_from_data(self):
        result = resolve_city_iata("Athens")
        assert result is not None
        assert len(result) == 3
        assert result.isupper()

    def test_unknown_city_returns_none(self):
        assert resolve_city_iata("Nowheresville XYZ") is None

    def test_empty_string(self):
        assert resolve_city_iata("") is None

    def test_none_input(self):
        assert resolve_city_iata(None) is None
