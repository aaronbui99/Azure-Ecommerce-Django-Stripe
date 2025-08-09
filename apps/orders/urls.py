from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/', views.UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/success/', views.OrderSuccessView.as_view(), name='success'),
]