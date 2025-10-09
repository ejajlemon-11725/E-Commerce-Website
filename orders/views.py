from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem
from .cart import Cart
from catalog.models import Product

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import Order, OrderItem
from .cart import Cart
from catalog.models import Product


def checkout_view(request):
    cart = Cart(request)

    # 1️⃣ Prevent empty cart checkout
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("catalog:home")

    # 2️⃣ Handle checkout form submission
    if request.method == "POST":
        email = request.POST.get("email")

        # ✅ Create the order
        order = Order.objects.create(
            email=email,
            total=cart.grand_total
        )

        # ✅ Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],
                price=item["price"],
            )

        # ✅ Clear cart after checkout
        cart.clear()

        # ✅ Send confirmation email
        try:
            send_mail(
                subject="✅ Payment Successful",
                message=(
                    f"Hello,\n\nYour payment has been successfully processed.\n\n"
                    f"Order ID: {order.id}\n"
                    f"Amount Paid: ${order.total}\n\n"
                    f"Thank you for shopping with us!\n\n"
                    f"Best regards,\n{getattr(settings, 'SITE_NAME', 'Our Store')}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,  # won't crash even if email fails
            )
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")

        # ✅ Redirect to success page
        messages.success(request, "Your payment was successful! Confirmation email sent.")
        return redirect("orders:success")

    # 3️⃣ Render checkout form
    return render(request, "orders/checkout.html", {"cart": cart})



def success_view(request):
    return render(request, "orders/success.html")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.POST.get("qty", 1))  # ✅ ensure int
    except ValueError:
        qty = 1
    cart.add(product, qty=qty, override_qty=False)
    return redirect(request.META.get("HTTP_REFERER", reverse("orders:cart_detail")))


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.POST.get("qty", 1))  # ✅ ensure int
    except ValueError:
        qty = 1
    cart.update(product, qty=qty)
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("orders:cart_detail")


@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("orders:cart_detail")