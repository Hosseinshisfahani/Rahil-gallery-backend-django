"""DRF authentication that verifies Go-issued HS256 access JWTs."""

from __future__ import annotations

import uuid
from typing import Any

import jwt
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.request import Request

from identity.models import User, UserStatus


class GoJWTAuthentication(BaseAuthentication):
    """
    Validate Bearer tokens issued by Rahil-gallery-backend-go.

    Go claims: sub (user UUID), email, role, exp, iat, jti — no iss/aud/token_type.
    """

    keyword = "Bearer"
    www_authenticate_realm = "api"

    def authenticate(self, request: Request):
        header = get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "invalid authorization header"}
            )

        raw = parts[1]
        claims = self._decode(raw)
        user = self._resolve_user(claims)
        return (user, claims)

    def authenticate_header(self, request: Request) -> str:
        return f'{self.keyword} realm="{self.www_authenticate_realm}"'

    def _decode(self, token: str) -> dict[str, Any]:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "invalid or expired token"}
            ) from exc

        if header.get("alg") != "HS256":
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "unexpected signing method"}
            )

        try:
            return jwt.decode(
                token,
                settings.JWT_ACCESS_SECRET,
                algorithms=["HS256"],
                options={
                    "require": ["exp", "sub"],
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
        except jwt.ExpiredSignatureError as exc:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "invalid or expired token"}
            ) from exc
        except jwt.PyJWTError as exc:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "invalid or expired token"}
            ) from exc

    def _resolve_user(self, claims: dict[str, Any]) -> User:
        sub = claims.get("sub")
        if not sub:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "invalid subject"}
            )
        try:
            user_id = uuid.UUID(str(sub))
        except (TypeError, ValueError) as exc:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "invalid subject"}
            ) from exc

        try:
            user = User.objects.select_related("role").get(pk=user_id)
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "user not found"}
            ) from exc

        if user.deleted_at is not None or user.status != UserStatus.ACTIVE:
            raise exceptions.AuthenticationFailed(
                detail={"code": "unauthorized", "message": "user inactive or banned"}
            )

        # Prefer live DB role; fall back to JWT claim for permission helpers
        jwt_role = claims.get("role")
        if jwt_role:
            user._jwt_role = jwt_role  # type: ignore[attr-defined]

        return user
