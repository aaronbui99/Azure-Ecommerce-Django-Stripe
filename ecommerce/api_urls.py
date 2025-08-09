"""API URL Configuration"""
from django.urls import path, include

urlpatterns = [
    path('v1/products/', include('apps.products.api.urls')),
    path('v1/orders/', include('apps.orders.api.urls')),
    path('v1/payments/', include('apps.payments.api.urls')),
]