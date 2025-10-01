from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', CategoryListView.as_view(), name='category_list'),
    path('<slug:category_slug>/', ProductListView.as_view(), name='product_list'),
    path('<slug:category_slug>/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('', views.product_list, name='catalog'),
    path('', views.home, name='home'),
]
