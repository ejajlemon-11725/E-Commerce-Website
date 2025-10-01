from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem
from core.cart import Cart
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from catalog.models import Product
from .cart import Cart

def checkout_view(request):
    cart = Cart(request)
    if request.method == "POST":
        email = request.POST.get("email")
        if not len(cart):
            messages.error(request, "Cart is empty.")
            return redirect("product_list")
        order = Order.objects.create(email=email, total=cart.total_price())
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"],
            )
        # clear cart before payment; mark paid in payments flow
        request.session["cart"] = {}
        return redirect("payment_create", order_id=order.id)
    return render(request, "orders/checkout.html", {"cart": cart})

def success_view(request):
    return render(request, "orders/success.html")

def cart_detail(request):
    # Example: cart logic
    cart_count = 0  # replace with real cart count if you have a cart session
    context = {
        "cart_count": cart_count,
    }
    return render(request, "orders/cart_detail.html", context)

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart.html", {"cart": cart})

@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    qty = int(request.POST.get("quantity", 1))
    cart.add(product=product, quantity=qty, override_quantity=False)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("cart_detail")
    return redirect(next_url)

@require_POST
def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    qty = max(1, int(request.POST.get("quantity", 1)))
    cart.add(product=product, quantity=qty, override_quantity=True)
    return redirect("cart_detail")

@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("cart_detail")