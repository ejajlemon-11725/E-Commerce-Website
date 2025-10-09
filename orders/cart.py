from decimal import Decimal
from catalog.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product: Product, qty=1, override_qty=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "qty": 0,
                "price": str(product.price)  # still string for JSON, converted later
            }

        if override_qty:
            self.cart[product_id]["qty"] = qty
        else:
            self.cart[product_id]["qty"] += qty

        self.save()

    def update(self, product: Product, qty):
        """
        Update product quantity in the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]["qty"] = qty
            self.save()

    def remove(self, product: Product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """
        Remove all items from the cart.
        """
        self.session["cart"] = {}
        self.session.modified = True

    def save(self):
        """
        Mark the session as modified to make sure it gets saved.
        """
        self.session["cart"] = self.cart
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)].copy()
            item["product"] = product
            item["total_price"] = Decimal(item["price"]) * item["qty"]  # convert string to Decimal
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item["qty"] for item in self.cart.values())

    @property
    def total_price(self):
        """
        Get the total cost of the cart.
        """
        return sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())

    @property
    def is_empty(self):
        """
        Check if the cart is empty.
        """
        return len(self.cart) == 0

    @property
    def grand_total(self):
        """
        Alias for total_price to maintain compatibility with checkout_view.
        """
        return self.total_price
