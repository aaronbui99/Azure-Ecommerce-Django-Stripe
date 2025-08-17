from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.PaymentProcessView.as_view(), name='process'),
    path('create-intent/', views.CreatePaymentIntentView.as_view(), name='create_intent'),
    path('confirm/', views.PaymentConfirmView.as_view(), name='confirm'),
    path('webhook/', views.StripeWebhookView.as_view(), name='webhook'),
    path('methods/', views.PaymentMethodListView.as_view(), name='methods'),
    path('methods/add/', views.AddPaymentMethodView.as_view(), name='add_method'),
    path('methods/<int:pk>/delete/', views.DeletePaymentMethodView.as_view(), name='delete_method'),
    path('test-order/', views.CreateTestOrderView.as_view(), name='create_test_order'),
]