from django.urls import path

from commerce.views import MyCartItemDetailView, MyCartItemsView, MyCartView

urlpatterns = [
    path("carts/me", MyCartView.as_view(), name="cart-me"),
    path("carts/me/items", MyCartItemsView.as_view(), name="cart-me-items"),
    path(
        "carts/me/items/<uuid:item_id>",
        MyCartItemDetailView.as_view(),
        name="cart-me-item-detail",
    ),
]
