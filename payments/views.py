from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from orders.models import Order
import stripe

def payment_create(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY or None

    # Dev fallback: if no Stripe key, mark paid directly
    if not stripe.api_key:
        order.status = Order.PAID
        order.save()
        return redirect("order_success")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": settings.CURRENCY,
                "product_data": {"name": f"Order #{order.id}"},
                "unit_amount": int(order.total * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri(reverse("order_success")),
        cancel_url=request.build_absolute_uri(reverse("checkout")),
    )
    return redirect(session.url, code=303)

def stripe_webhook(request):
    # TODO: verify signature & update order status
    return HttpResponse(status=200)
