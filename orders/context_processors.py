# orders/context_processors.py
from .cart import Cart

def cart_summary(request):
    cart = Cart(request)
    return {
        "cart_quantity": len(cart),
        "cart_subtotal": cart.subtotal,
    }
