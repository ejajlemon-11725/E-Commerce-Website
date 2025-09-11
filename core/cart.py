from decimal import Decimal
from catalog.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product_id, quantity=1, override=False):
        product_id = str(product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": "0.00"}
        if override:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        p = Product.objects.get(pk=product_id)
        self.cart[product_id]["price"] = str(p.price)
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            item["product"] = product
            item["price"] = Decimal(item["price"])
            item["total"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(i["quantity"] for i in self.cart.values())

    def total_price(self):
        return sum(Decimal(i["price"]) * i["quantity"] for i in self.cart.values())

    def is_empty(self):
        return len(self) == 0
