from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("success/", views.success_view, name="order_success"),
    path("cart/", views.cart_detail, name="cart"),
     path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="cart_add"),
    path("cart/update/<int:product_id>/", views.update_cart, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="cart_remove"),

]
