from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-intent/', PaymentViewSet.as_view({'post': 'create_intent'}), name='create_intent'),
    path('confirm/', PaymentViewSet.as_view({'post': 'confirm_payment'}), name='confirm_payment'),
]