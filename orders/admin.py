from django.contrib import admin
from .models import Order, OrderItem, Address

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","status","email","total","created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]

admin.site.register(Address)
