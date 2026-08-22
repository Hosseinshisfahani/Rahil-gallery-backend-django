from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from catalog.models import ProductVariant
from commerce.models import Cart, CartItem, CartStatus
from commerce.serializers import (
    AddCartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)
from core.exceptions import fail, ok


def get_or_create_active_cart(user) -> Cart:
    cart = (
        Cart.objects.filter(user=user, status=CartStatus.ACTIVE)
        .prefetch_related("items")
        .first()
    )
    if cart:
        return cart
    return Cart.objects.create(user=user, status=CartStatus.ACTIVE)


class MyCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_active_cart(request.user)
        cart = Cart.objects.prefetch_related("items").get(pk=cart.pk)
        return ok(CartSerializer(cart).data)


class MyCartItemsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        ser = AddCartItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        try:
            variant = ProductVariant.objects.get(pk=data["variant_id"], is_active=True)
        except ProductVariant.DoesNotExist:
            return fail("not_found", "variant not found or inactive", status=404)

        cart = get_or_create_active_cart(request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": data["quantity"],
                "unit_price_snapshot": data["unit_price_snapshot"],
            },
        )
        if not created:
            item.quantity += data["quantity"]
            item.unit_price_snapshot = data["unit_price_snapshot"]
            item.save(update_fields=["quantity", "unit_price_snapshot", "updated_at"])

        cart = Cart.objects.prefetch_related("items").get(pk=cart.pk)
        return ok(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED if created else 200,
        )


class MyCartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _owned_item(self, request, item_id) -> CartItem:
        cart = get_or_create_active_cart(request.user)
        return get_object_or_404(CartItem, pk=item_id, cart=cart)

    def patch(self, request, item_id):
        ser = UpdateCartItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        item = self._owned_item(request, item_id)
        item.quantity = ser.validated_data["quantity"]
        item.save(update_fields=["quantity", "updated_at"])
        cart = Cart.objects.prefetch_related("items").get(pk=item.cart_id)
        return ok(CartSerializer(cart).data)

    def delete(self, request, item_id):
        item = self._owned_item(request, item_id)
        cart_id = item.cart_id
        item.delete()
        cart = Cart.objects.prefetch_related("items").get(pk=cart_id)
        return ok(CartSerializer(cart).data)
