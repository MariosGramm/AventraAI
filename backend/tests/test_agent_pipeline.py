"""Tests for the agent pipeline's pure helper methods."""

import json
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

from app.agent.agent_pipeline import TravelAgentPipeline
from app.enums import ChatRole, SubscriptionTier
from app.models import User


def _make_user(tier=SubscriptionTier.FREE) -> User:
    return User(
        first_name="Test", last_name="User",
        email="test@test.com", hashed_password="",
        subscription_tier=tier,
    )


class TestParseSearchResponse:
    """Test JSON parsing of LLM search output."""

    def setup_method(self):
        with patch.object(TravelAgentPipeline, "__init__", lambda self: None):
            self.pipeline = TravelAgentPipeline()

    def test_valid_json(self):
        raw = json.dumps({"packages": [{"tier": "standard"}]})
        result = self.pipeline._parse_search_response(raw)
        assert result["packages"][0]["tier"] == "standard"

    def test_json_with_code_fences(self):
        raw = '```json\n{"packages": [{"tier": "budget"}]}\n```'
        result = self.pipeline._parse_search_response(raw)
        assert result["packages"][0]["tier"] == "budget"

    def test_invalid_json_returns_empty(self):
        result = self.pipeline._parse_search_response("not json at all")
        assert result == {}

    def test_empty_string_returns_empty(self):
        result = self.pipeline._parse_search_response("")
        assert result == {}


class TestFormatHistory:

    def setup_method(self):
        with patch.object(TravelAgentPipeline, "__init__", lambda self: None):
            self.pipeline = TravelAgentPipeline()

    def test_empty_history(self):
        result = self.pipeline._format_history_as_text([])
        assert result == "No previous conversation."

    def test_with_messages(self):
        history = [
            SimpleNamespace(role=ChatRole.USER, content="Hello"),
            SimpleNamespace(role=ChatRole.ASSISTANT, content="Hi there!"),
        ]
        result = self.pipeline._format_history_as_text(history)
        assert "User: Hello" in result
        assert "Assistant: Hi there!" in result

    def test_format_as_messages(self):
        from langchain_core.messages import HumanMessage, AIMessage
        history = [
            SimpleNamespace(role=ChatRole.USER, content="Hi"),
            SimpleNamespace(role=ChatRole.ASSISTANT, content="Hello"),
        ]
        messages = self.pipeline._format_history_as_messages(history)
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)


class TestGetLlm:

    def setup_method(self):
        with patch.object(TravelAgentPipeline, "__init__", lambda self: None):
            self.pipeline = TravelAgentPipeline()
            from app.agent.config import Config
            self.pipeline.config = Config()

    def test_free_user_gets_mini(self):
        llm = self.pipeline._get_llm(_make_user(SubscriptionTier.FREE), "chat")
        assert "mini" in llm.model_name

    def test_paid_user_gets_full(self):
        llm = self.pipeline._get_llm(_make_user(SubscriptionTier.PAID), "chat")
        assert "mini" not in llm.model_name

    def test_search_mode_lower_temperature(self):
        llm = self.pipeline._get_llm(_make_user(), "search")
        assert llm.temperature == 0.2


class TestTranslateDestination:

    def setup_method(self):
        with patch.object(TravelAgentPipeline, "__init__", lambda self: None):
            self.pipeline = TravelAgentPipeline()
            from app.agent.config import Config
            self.pipeline.config = Config()

    def test_ascii_passthrough(self):
        assert self.pipeline._translate_destination("Prague") == "Prague"
        assert self.pipeline._translate_destination("New York") == "New York"
