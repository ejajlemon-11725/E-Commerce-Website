# shop/admin.py
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "old_price", "discount_percent", "is_flash_sale", "is_featured", "stock")
    list_filter = ("is_flash_sale", "is_featured", "category")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
