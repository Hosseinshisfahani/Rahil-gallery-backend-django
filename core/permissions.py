from __future__ import annotations

from typing import Optional

from rest_framework.permissions import BasePermission


def _role_name(user) -> Optional[str]:
    jwt_role = getattr(user, "_jwt_role", None)
    if jwt_role:
        return str(jwt_role)
    try:
        return user.role.name
    except Exception:
        return None


class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return _role_name(request.user) in {"admin", "staff"}


class IsAuthenticatedCustomer(BasePermission):
    """Any authenticated active user (customer, staff, or admin)."""

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)
