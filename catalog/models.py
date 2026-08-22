import uuid

from django.db import models


class Product(models.Model):
    """Go-owned catalog product — read-only stub for FKs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=280)
    status = models.CharField(max_length=20)
    base_price = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="IRR")
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "products"

    def __str__(self) -> str:
        return self.name


class ProductVariant(models.Model):
    """Go-owned product_variants — read-only stub for cart/order FKs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        db_column="product_id",
        related_name="+",
    )
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=150)
    size_label = models.CharField(max_length=50, null=True, blank=True)
    color_label = models.CharField(max_length=50, null=True, blank=True)
    price_adjustment = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "product_variants"

    def __str__(self) -> str:
        return self.name


class UserAddress(models.Model):
    """Go-owned user_addresses — read-only stub for order FKs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    address_type = models.CharField(max_length=20)
    recipient_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    address_line = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "user_addresses"


class Customer(models.Model):
    """Go-owned CRM customers — read-only stub."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=255, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "customers"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
