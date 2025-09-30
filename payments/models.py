# payments/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Payment(models.Model):
    GATEWAYS = (("bkash","bKash"), ("nagad","Nagad"))
    STATUSES = (
        ("initiated","initiated"),
        ("redirected","redirected"),
        ("executed","executed"),      # (bKash execute OK)
        ("success","success"),
        ("failed","failed"),
        ("cancelled","cancelled"),
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL)
    gateway = models.CharField(max_length=20, choices=GATEWAYS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="BDT")
    invoice_no = models.CharField(max_length=80, blank=True)
    provider_payment_id = models.CharField(max_length=120, blank=True)   # bKash paymentID / Nagad payment_ref_id
    status = models.CharField(max_length=20, choices=STATUSES, default="initiated")
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def mark(self, status, meta=None):
        self.status = status
        if meta:
            self.meta = {**self.meta, **meta}
        self.save(update_fields=["status","meta","updated_at"])

    def __str__(self):
        return f"{self.gateway} {self.amount} {self.currency} [{self.status}]"
