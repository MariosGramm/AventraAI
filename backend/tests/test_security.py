"""Tests for security utilities."""

from datetime import timedelta

from app.core.security import create_access_token, get_password_hash, verify_password


class TestPasswordHashing:

    def test_hash_and_verify(self):
        password = "securepassword123"
        hashed = get_password_hash(password)
        verified, _ = verify_password(password, hashed)
        assert verified

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct_password")
        verified, _ = verify_password("wrong_password", hashed)
        assert not verified

    def test_hash_is_not_plaintext(self):
        password = "mypassword"
        hashed = get_password_hash(password)
        assert hashed != password


class TestJWT:

    def test_create_and_decode_token(self):
        import jwt
        from app.core.config import settings
        from app.core.security import ALGORITHM

        user_id = "test-user-id-123"
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(hours=1),
        )
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == user_id

    def test_token_has_expiry(self):
        import jwt
        from app.core.config import settings
        from app.core.security import ALGORITHM

        token = create_access_token(subject="user", expires_delta=timedelta(hours=1))
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
