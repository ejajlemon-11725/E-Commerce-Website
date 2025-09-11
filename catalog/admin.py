from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name","parent")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title","category","price","stock","is_active","created_at")
    list_filter = ("category","is_active")
    search_fields = ("title","description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]
