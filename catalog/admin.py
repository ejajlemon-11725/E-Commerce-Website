from django.contrib import admin
from .models import Category,Product

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "product_count")

    def product_count(self, obj):
        return obj.products.count()   # adjust related_name if different
    product_count.short_description = "Products"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "old_price", "discount_percentage")
    list_filter = ("category",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
