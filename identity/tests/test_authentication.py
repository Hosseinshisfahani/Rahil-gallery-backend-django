from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
import uuid

import jwt
from django.test import SimpleTestCase, override_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from identity.authentication import GoJWTAuthentication
from identity.models import UserStatus


@override_settings(JWT_ACCESS_SECRET="unit-test-secret-at-least-32-chars!!")
class GoJWTAuthenticationTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = GoJWTAuthentication()
        self.secret = "unit-test-secret-at-least-32-chars!!"
        self.user_id = uuid.uuid4()

    def _token(self, **extra):
        payload = {
            "sub": str(self.user_id),
            "email": "admin@example.com",
            "role": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
        }
        payload.update(extra)
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def test_missing_header_returns_none(self):
        request = self.factory.get("/api/v1/carts/me")
        self.assertIsNone(self.auth.authenticate(request))

    def test_invalid_scheme(self):
        request = self.factory.get(
            "/api/v1/carts/me", HTTP_AUTHORIZATION="Token abc"
        )
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    @patch("identity.authentication.User.objects")
    def test_valid_token_resolves_user(self, mock_objects):
        user = MagicMock()
        user.deleted_at = None
        user.status = UserStatus.ACTIVE
        mock_objects.select_related.return_value.get.return_value = user

        request = self.factory.get(
            "/api/v1/carts/me",
            HTTP_AUTHORIZATION=f"Bearer {self._token()}",
        )
        result_user, claims = self.auth.authenticate(request)
        self.assertIs(result_user, user)
        self.assertEqual(claims["sub"], str(self.user_id))
        self.assertEqual(claims["role"], "admin")
        self.assertEqual(getattr(user, "_jwt_role"), "admin")

    @patch("identity.authentication.User.objects")
    def test_banned_user_rejected(self, mock_objects):
        user = MagicMock()
        user.deleted_at = None
        user.status = UserStatus.BANNED
        mock_objects.select_related.return_value.get.return_value = user

        request = self.factory.get(
            "/api/v1/carts/me",
            HTTP_AUTHORIZATION=f"Bearer {self._token()}",
        )
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_expired_token_rejected(self):
        token = self._token(exp=datetime.now(timezone.utc) - timedelta(minutes=1))
        request = self.factory.get(
            "/api/v1/carts/me", HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_non_hs256_rejected(self):
        import base64
        import json

        header = (
            base64.urlsafe_b64encode(
                json.dumps({"alg": "none", "typ": "JWT"}).encode()
            )
            .rstrip(b"=")
            .decode()
        )
        payload = (
            base64.urlsafe_b64encode(
                json.dumps(
                    {
                        "sub": str(self.user_id),
                        "exp": int(
                            (
                                datetime.now(timezone.utc) + timedelta(minutes=5)
                            ).timestamp()
                        ),
                    }
                ).encode()
            )
            .rstrip(b"=")
            .decode()
        )
        token = f"{header}.{payload}."
        request = self.factory.get(
            "/api/v1/carts/me", HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)
