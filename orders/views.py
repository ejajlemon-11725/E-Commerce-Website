from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import Order, OrderItem
from .cart import Cart
from catalog.models import Product


def checkout_view(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("catalog:home")  # adjust if needed

    if request.method == "POST":
        email = request.POST.get("email")

        # Create order
        order = Order.objects.create(email=email, total=cart.grand_total)

        # Save items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],  # correct: your cart uses 'qty'
                price=item["price"],
            )

        # Clear cart
        cart.clear()

        return redirect("payments:payment_create", order_id=order.id)

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
