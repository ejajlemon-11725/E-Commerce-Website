from django.urls import path
from . import views

urlpatterns = [
    path("create/<int:order_id>/", views.payment_create, name="payment_create"),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
]
