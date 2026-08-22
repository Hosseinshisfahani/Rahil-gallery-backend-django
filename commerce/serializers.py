from decimal import Decimal

from rest_framework import serializers

from commerce.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    variant_id = serializers.UUIDField(source="variant.id", read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "variant_id",
            "quantity",
            "unit_price_snapshot",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "status",
            "expires_at",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AddCartItemSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price_snapshot = serializers.DecimalField(
        max_digits=14, decimal_places=2, min_value=Decimal("0")
    )


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
