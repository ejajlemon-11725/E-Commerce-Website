from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Order, OrderItem
from core.cart import Cart
from django.views.decorators.http import require_POST
from django.urls import reverse
from catalog.models import Product
from .cart import Cart



# orders/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Order, OrderItem
from core.cart import Cart
from django.views.decorators.http import require_POST
from django.urls import reverse
from catalog.models import Product
from .cart import Cart


def checkout_view(request):
    cart = Cart(request)

    # If cart is empty, redirect back with error
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect("catalog:home")  # adjust if your homepage URL is different

    if request.method == "POST":
        email = request.POST.get("email")

        # Use cart.grand_total instead of get_total()
        order = Order.objects.create(email=email, total=cart.grand_total)

        # Save all items from cart to OrderItem
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],   # note: your Cart uses 'qty'
                price=item["price"],
            )

        # Clear cart after order
        cart.clear()

        # Redirect to payment or success page
        return redirect("payments:payment_create", order_id=order.id)

    # GET request renders checkout page
    return render(request, "orders/checkout.html", {"cart": cart})



def success_view(request):
    return render(request, "orders/success.html")





# Updated cart_detail function for actual cart display
def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    qty = request.POST.get("qty", 1)
    cart.add(product, qty=qty, override_qty=False)
    # back to same page if referrer exists; else go to cart
    return redirect(request.META.get("HTTP_REFERER", reverse("orders:cart_detail")))

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    qty = request.POST.get("qty", 1)
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