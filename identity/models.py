import uuid
from typing import List

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    BANNED = "banned", "Banned"


class Role(models.Model):
    """Go-owned `roles` — read-only from Django."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "roles"

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = False

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class User(AbstractBaseUser):
    """
    Go-owned `users` table (managed=False).
    Login / password / refresh tokens stay on the Go API.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role,
        on_delete=models.DO_NOTHING,
        db_column="role_id",
        related_name="+",
    )
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    # AbstractBaseUser.password → Go column password_hash
    password = models.CharField(max_length=255, db_column="password_hash", null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
    )
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True, db_column="last_login_at")
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = UserManager()

    # Email is nullable / partially unique in Go; authenticate via JWT `sub` → id
    USERNAME_FIELD = "id"
    REQUIRED_FIELDS: List[str] = []

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self) -> str:
        return self.email or self.phone or str(self.id)

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and self.deleted_at is None

    @property
    def is_staff(self) -> bool:
        try:
            return self.role.name in {"admin", "staff"}
        except Exception:
            return False

    @property
    def is_superuser(self) -> bool:
        try:
            return self.role.name == "admin"
        except Exception:
            return False

    def has_perm(self, perm, obj=None) -> bool:
        return self.is_staff

    def has_module_perms(self, app_label) -> bool:
        return self.is_staff

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name
