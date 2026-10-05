import uuid

from django.conf import settings
from django.db import models

from catalog.models import ProductVariant, UserAddress


class CartStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    MERGED = "merged", "Merged"
    ABANDONED = "abandoned", "Abandoned"
    CONVERTED = "converted", "Converted"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    AUTHORIZED = "authorized", "Authorized"
    PAID = "paid", "Paid"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class PaymentProvider(models.TextChoices):
    ZARINPAL = "zarinpal", "Zarinpal"
    IDPAY = "idpay", "IDPay"
    MANUAL = "manual", "Manual"
    OTHER = "other", "Other"


class DiscountType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED_AMOUNT = "fixed_amount", "Fixed amount"


class JewelryType(models.TextChoices):
    RING = "ring", "Ring"
    NECKLACE = "necklace", "Necklace"
    BRACELET = "bracelet", "Bracelet"
    EARRING = "earring", "Earring"
    PENDANT = "pendant", "Pendant"
    ANKLET = "anklet", "Anklet"
    BROOCH = "brooch", "Brooch"
    SET = "set", "Set"
    OTHER = "other", "Other"


class MetalType(models.TextChoices):
    GOLD_YELLOW = "gold_yellow", "Gold yellow"
    GOLD_WHITE = "gold_white", "Gold white"
    GOLD_ROSE = "gold_rose", "Gold rose"
    SILVER = "silver", "Silver"
    PLATINUM = "platinum", "Platinum"
    TITANIUM = "titanium", "Titanium"
    MIXED = "mixed", "Mixed"
    OTHER = "other", "Other"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="user_id",
        related_name="carts",
    )
    guest_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=CartStatus.choices,
        default=CartStatus.ACTIVE,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "carts"

    def __str__(self) -> str:
        return str(self.id)


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        db_column="cart_id",
        related_name="items",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price_snapshot = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"],
                name="cart_items_unique_variant",
            ),
        ]


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="user_id",
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="IRR")
    customer_note = models.TextField(null=True, blank=True)
    shipping_address = models.ForeignKey(
        UserAddress,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="shipping_address_id",
        related_name="+",
    )
    billing_address = models.ForeignKey(
        UserAddress,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        db_column="billing_address_id",
        related_name="+",
    )
    placed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "orders"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="items",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=150)
    sku = models.CharField(max_length=64)
    jewelry_type = models.CharField(max_length=20, choices=JewelryType.choices)
    metal_type = models.CharField(
        max_length=20, choices=MetalType.choices, null=True, blank=True
    )
    karat = models.SmallIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)
    weight_grams = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )

    class Meta:
        managed = True
        db_table = "order_items"


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="status_history",
    )
    from_status = models.CharField(
        max_length=20, choices=OrderStatus.choices, null=True, blank=True
    )
    to_status = models.CharField(max_length=20, choices=OrderStatus.choices)
    note = models.TextField(null=True, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="changed_by",
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "order_status_history"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="payments",
    )
    provider = models.CharField(max_length=20, choices=PaymentProvider.choices)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="IRR")
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "payments"


class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=14, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "coupons"


class CouponRedemption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.DO_NOTHING,
        db_column="coupon_id",
        related_name="redemptions",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        db_column="order_id",
        related_name="coupon_redemptions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        db_column="user_id",
        related_name="+",
    )
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "coupon_redemptions"
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                name="coupon_redemptions_order_unique",
            ),
        ]
