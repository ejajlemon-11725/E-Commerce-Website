# orders/context_processors.py
from .cart import Cart

def cart_summary(request):
    cart = Cart(request)
    return {
        "cart": cart,                 # ✅ return the cart object
        "cart_count": len(cart),      # optional shortcut
        "cart_subtotal": cart.subtotal,
    }
