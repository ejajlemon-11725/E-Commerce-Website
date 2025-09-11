from django.shortcuts import render, redirect
from catalog.models import Product
from .cart import Cart

def home(request):
    qs = Product.objects.filter(is_active=True)[:12]
    return render(request, "core/home.html", {"products": qs})

def add_to_cart(request, pk):
    cart = Cart(request)
    cart.add(pk, quantity=1)
    return redirect(request.META.get("HTTP_REFERER", "/"))

def remove_from_cart(request, pk):
    cart = Cart(request)
    cart.remove(pk)
    return redirect("view_cart")

def view_cart(request):
    cart = Cart(request)
    return render(request, "core/cart.html", {"cart": cart})
