from django.db import models
from django.conf import settings
from catalog.models import Product

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=120)
    line1 = models.CharField(max_length=200)
    line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60, default="Bangladesh")
    phone = models.CharField(max_length=30, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name}, {self.line1}"

class Order(models.Model):
    PENDING, PAID, FAILED, REFUNDED = "PENDING","PAID","FAILED","REFUNDED"
    STATUS_CHOICES = [(PENDING,"Pending"),(PAID,"Paid"),(FAILED,"Failed"),(REFUNDED,"Refunded")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    email = models.EmailField()
    shipping_address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.pk} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} x{self.quantity}"
