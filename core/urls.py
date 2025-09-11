from django.urls import path
from . import views
from orders.views import checkout_view  # reuse orders' checkout

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", checkout_view, name="checkout"),
]
