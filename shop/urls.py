# shop/urls.py
from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("add-to-cart/<int:pk>/", views.add_to_cart, name="add_to_cart"),
]
