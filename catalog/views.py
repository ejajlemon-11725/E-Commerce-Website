from django.views.generic import ListView, DetailView
from .models import Product

class ProductListView(ListView):
    model = Product
    paginate_by = 12
    template_name = "catalog/product_list.html"

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs

class ProductDetailView(DetailView):
    model = Product
    slug_field = "slug"
    template_name = "catalog/product_detail.html"
