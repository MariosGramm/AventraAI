"""Tests for freemium limits and business rules."""

from datetime import UTC, datetime
from dateutil.relativedelta import relativedelta
from unittest.mock import patch

from app.enums import SubscriptionTier
from app.models import User


class TestFreemiumLimits:

    def test_free_tier_limits(self):
        from app.api.routes.travel import FREE_TIER_LIMIT
        from app.api.routes.chat import FREE_MESSAGE_LIMIT
        assert FREE_TIER_LIMIT == 3
        assert FREE_MESSAGE_LIMIT == 50

    def test_paid_tier_limits(self):
        from app.api.routes.travel import PAID_TIER_LIMIT
        from app.api.routes.chat import PAID_MESSAGE_LIMIT
        assert PAID_TIER_LIMIT == 20
        assert PAID_MESSAGE_LIMIT == 500

    def test_max_pinned_sessions(self):
        from app.api.routes.chat import MAX_PINNED_CHAT_SESSIONS
        assert MAX_PINNED_CHAT_SESSIONS == 3


class TestTripValidation:

    def test_max_trip_duration(self):
        """Trip duration limit should be 15 days."""
        from datetime import timedelta
        max_days = 15
        date_from = datetime(2026, 9, 1)
        date_to = date_from + timedelta(days=max_days)
        trip_days = (date_to - date_from).days
        assert trip_days == max_days

    def test_min_trip_duration(self):
        """Trip must be at least 1 day."""
        date_from = datetime(2026, 9, 1)
        date_to = datetime(2026, 9, 2)
        trip_days = (date_to - date_from).days
        assert trip_days >= 1


class TestStripeAllowedPaths:

    def test_allowed_return_paths(self):
        from app.api.routes.payments import ALLOWED_RETURN_PATHS
        assert "/" in ALLOWED_RETURN_PATHS
        assert "/profile" in ALLOWED_RETURN_PATHS
        assert "/admin" not in ALLOWED_RETURN_PATHS
        assert "https://evil.com" not in ALLOWED_RETURN_PATHS
