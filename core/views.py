from django.conf import settings
from django.shortcuts import redirect
from catalog.models import Product
from .cart import Cart
from django.shortcuts import render

def home(request):
    # This is the diagnostic line we need to run
    print(f"--- The current DEBUG setting is: {settings.DEBUG} ---")

    products = [
        {'title': 'Mouse', 'price': 649, 'image': {'url': '/static/images/mouse.jpg'}},
        {'title': 'A4 Tech Keyboard', 'price': 799, 'image': {'url': '/static/images/keyboard.jpg'}},
        {'title': 'Electric Wire', 'price': 5, 'image': {'url': '/static/images/wire.jpg'}},
        {'title': 'Circuit Board', 'price': 99, 'image': {'url': '/static/images/board.jpg'}},
        {'title': 'Essential Multimeter', 'price': 749, 'image': {'url': '/static/images/multimeter.jpg'}},
        {'title': 'Pen Holder', 'price': 78, 'image': {'url': '/static/images/pen_holder.jpg'}},
        {'title': 'The Economics Book', 'price': 350, 'image': {'url': '/static/images/economics_book.jpg'}},
        {'title': 'Circuit Analysis Book', 'price': 380, 'image': {'url': '/static/images/circuit_book.jpg'}},
    ]

    context = {
        'products': products
    }
    return render(request, 'home.html', context)

# (The rest of your views like add_to_cart can remain unchanged)

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
