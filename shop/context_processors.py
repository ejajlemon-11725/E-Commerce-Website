# shop/context_processors.py
def cart(request):
    cart = request.session.get('cart', {})  # get cart from session
    count = 0
    for v in cart.values():
        if isinstance(v, int):          # normal case: quantity
            count += v
        elif isinstance(v, dict) and 'qty' in v:  # sometimes cart stores {'qty': X, ...}
            count += v['qty']
    return {'cart_count': count}
