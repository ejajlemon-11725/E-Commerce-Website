from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # Checkout (no order_id needed)
    path("checkout/", views.checkout_view, name="checkout"),

    # Generic payment creation (optional, still requires order_id)
    path("create/<int:order_id>/", views.payment_create, name="payment_create"),

    # Stripe webhook
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),

    # bKash
    path("bkash/create/<int:order_id>/", views.bkash_create, name="bkash_create"),
    path("bkash/callback/", views.bkash_callback, name="bkash_callback"),

    # Nagad
    path("nagad/create/<int:order_id>/", views.nagad_create, name="nagad_create"),
    path("nagad/callback/", views.nagad_callback, name="nagad_callback"),

    # Generic results
    path("success/", views.payment_success, name="success"),
    path("fail/", views.payment_fail, name="fail"),
]
