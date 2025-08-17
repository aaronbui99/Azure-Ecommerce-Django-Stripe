from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartViewSet, CartCountView, UpdateCartAPIView

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('cart-count/', CartCountView.as_view(), name='cart-count'),
    path('update-cart/', UpdateCartAPIView.as_view(), name='update-cart'),
]