from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from catalog import views as catalog_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path(" ", include("core.urls")),
    path('catalog/', include('catalog.urls')),
    path("orders/", include("orders.urls")),
    path("payments/", include("payments.urls", namespace="payments")),
    path('', catalog_views.home, name='home'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




