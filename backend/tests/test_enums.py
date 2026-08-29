"""Tests for enum consistency and coverage."""

from app.enums import (
    ActivityType,
    ChatRole,
    Currency,
    PartOfDay,
    SearchSessionStatus,
    SubscriptionTier,
    TravelPackageTier,
    TripType,
)


class TestEnums:

    def test_subscription_tiers(self):
        assert SubscriptionTier.FREE == "free"
        assert SubscriptionTier.PAID == "paid"

    def test_chat_roles(self):
        assert ChatRole.USER == "user"
        assert ChatRole.ASSISTANT == "assistant"

    def test_travel_package_tiers(self):
        assert set(TravelPackageTier) == {"budget", "standard", "luxury"}

    def test_part_of_day(self):
        assert set(PartOfDay) == {"morning", "afternoon", "evening"}

    def test_activity_types(self):
        assert set(ActivityType) == {"sightseeing", "food", "adventure"}

    def test_currencies(self):
        assert "EUR" in set(Currency)
        assert "USD" in set(Currency)

    def test_trip_types(self):
        assert "solo" in set(TripType)
        assert "family" in set(TripType)
        assert "romantic" in set(TripType)
        assert "friends" in set(TripType)

    def test_search_session_status(self):
        assert set(SearchSessionStatus) == {"pending", "completed", "failed"}
