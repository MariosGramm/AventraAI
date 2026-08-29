"""Tests for Places API caching and fallback logic."""

from unittest.mock import patch, MagicMock

from app.agent.infrastructure import places as places_module
from app.agent.infrastructure.places import PlacesService


class TestPlacesCache:

    def setup_method(self):
        places_module._places_cache.clear()
        places_module._details_cache.clear()
        places_module._photo_cache.clear()

    @patch("app.agent.infrastructure.places.requests.post")
    @patch("app.agent.infrastructure.places.requests.get")
    def test_search_caches_results(self, mock_get, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"places": [{"id": "abc", "displayName": {"text": "Test"}, "rating": 4.5}]}
        )

        svc = PlacesService()
        result1 = svc.get_places("Prague", "restaurants")
        result2 = svc.get_places("Prague", "restaurants")

        assert result1 == result2
        assert mock_post.call_count == 1  # second call served from cache

    @patch("app.agent.infrastructure.places.requests.get")
    def test_details_caches_results(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "abc", "displayName": {"text": "Test"}, "rating": 4.5}
        )

        svc = PlacesService()
        result1 = svc.get_place_details("abc")
        result2 = svc.get_place_details("abc")

        assert result1 == result2
        assert mock_get.call_count == 1

    @patch("app.agent.infrastructure.places.requests.get")
    def test_photo_caches_results(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"photoUri": "https://example.com/photo.jpg"}
        )

        svc = PlacesService()
        url1 = svc._get_photo_url("photos/test/123")
        url2 = svc._get_photo_url("photos/test/123")

        assert url1 == url2 == "https://example.com/photo.jpg"
        assert mock_get.call_count == 1

    def test_cache_key_case_insensitive(self):
        places_module._places_cache[("prague", "restaurants")] = [{"cached": True}]

        svc = PlacesService()
        result = svc.get_places("Prague", "Restaurants")
        assert result == [{"cached": True}]


class TestPlacesFallback:

    def setup_method(self):
        places_module._places_cache.clear()
        places_module._details_cache.clear()
        places_module._photo_cache.clear()

    @patch("app.agent.infrastructure.places.requests.post")
    @patch("app.agent.infrastructure.places.requests.get")
    def test_expired_place_id_falls_back_to_search(self, mock_get, mock_post):
        # First call: details returns 404 (expired ID)
        # Second call: details returns 200 (fresh ID)
        mock_get.side_effect = [
            MagicMock(status_code=404, text="Not found"),
            MagicMock(status_code=200, json=lambda: {"id": "fresh_id", "displayName": {"text": "Test Place"}, "rating": 4.0}),
        ]
        # Search for fresh ID
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"places": [{"id": "fresh_id"}]}
        )

        svc = PlacesService()
        result = svc.get_place_details("expired_id", place_name="Test Place", location="Prague")

        assert result["name"] == "Test Place"
        assert mock_post.call_count == 1  # fallback search was called

    @patch("app.agent.infrastructure.places.requests.get")
    def test_expired_id_no_name_returns_empty(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404, text="Not found")

        svc = PlacesService()
        result = svc.get_place_details("expired_id")

        assert result == {}
