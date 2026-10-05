import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class MaterialCategory(models.Model):
    """Material family, stored as a tree (for example Precious Stones → Emerald)."""

    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        allow_unicode=True,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sub_materials",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("material category")
        verbose_name_plural = _("material categories")

    def __str__(self) -> str:
        return self.name


class ProductType(models.Model):
    """Physical form of a piece (for example Ring, Bracelet, Crown)."""

    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        allow_unicode=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("product type")
        verbose_name_plural = _("product types")

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        allow_unicode=True,
    )
    sku = models.CharField(_("SKU"), max_length=64, unique=True)
    is_active = models.BooleanField(_("is active"), default=True)
    description = models.TextField(_("description"), blank=True)
    material_category = models.ForeignKey(
        MaterialCategory,
        verbose_name=_("material category"),
        on_delete=models.PROTECT,
        related_name="products",
    )
    product_type = models.ForeignKey(
        ProductType,
        verbose_name=_("product type"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="products",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self) -> str:
        return self.title


class ProductVariant(models.Model):
    """Structural variant of a product. Price, stock, and specs come later."""

    product = models.ForeignKey(
        Product,
        verbose_name=_("product"),
        on_delete=models.CASCADE,
        related_name="variants",
    )
    sku = models.CharField(
        _("SKU"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("product variant")
        verbose_name_plural = _("product variants")

    def __str__(self) -> str:
        return self.sku or str(self.pk)


class UserAddress(models.Model):
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
