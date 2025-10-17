from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView

app_name = 'catalog'

urlpatterns = [
    path('', CategoryListView.as_view(), name='category_list'),  # homepage for catalog
    path('<slug:category_slug>/', ProductListView.as_view(), name='product_list'),
    path('<slug:category_slug>/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
