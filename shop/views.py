# shop/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product

def home(request):
    flash_sale = Product.objects.filter(is_flash_sale=True)[:20]
    featured = Product.objects.filter(is_featured=True)[:12]
    return render(request, "shop/home.html", {"flash_sale": flash_sale, "featured": featured})

def add_to_cart(request, pk):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart
        return JsonResponse({"ok": True, "cart_count": sum(cart.values())})
    return redirect("shop:home")
