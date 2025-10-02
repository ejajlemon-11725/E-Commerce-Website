from decimal import Decimal

CART_SESSION_ID = "cart"

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, qty=1, override_qty=False):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {"qty": 0, "price": str(product.price)}
        if override_qty:
            self.cart[pid]["qty"] = int(qty)
        else:
            self.cart[pid]["qty"] += int(qty)
        self.save()

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def update(self, product, qty):
        pid = str(product.id)
        if pid in self.cart:
            q = max(1, int(qty))
            self.cart[pid]["qty"] = q
            self.save()

    def __iter__(self):
        from catalog.models import Product
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        for p in products:
            item = self.cart[str(p.id)]
            item["product"] = p
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["qty"]
            yield item

    def __len__(self):
        return sum(int(item["qty"]) for item in self.cart.values())

    @property
    def subtotal(self):
        return sum(Decimal(i.get("price", 0)) * i.get("qty", 0) for i in self.cart.values())

    @property
    def grand_total(self):
        return self.subtotal

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def save(self):
        # 🔥 FIXED: actually save cart into session
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True
