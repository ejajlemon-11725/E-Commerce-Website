from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, OrderItem
from core.cart import Cart

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
