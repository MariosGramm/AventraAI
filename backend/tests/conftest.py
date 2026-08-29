"""
Shared test fixtures for AventraAI backend tests.
"""

import uuid
from datetime import UTC, datetime

import pytest
from app.core.security import create_access_token, get_password_hash
from app.enums import AuthProvider, SubscriptionTier
from app.models import User


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
