from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Category

# -----------------------------
# Function-based views for home & catalog
# -----------------------------
def home(request):
    products = Product.objects.all()  # get all products for homepage
    return render(request, 'home.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {'products': products})

# -----------------------------
# Class-based views for categories and product details
# -----------------------------
class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'categories'

class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Product.objects.filter(category=self.category, is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = self.category
        return ctx

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return get_object_or_404(Product, category=category, slug=self.kwargs['slug'], is_active=True)
