#!/usr/bin/env python
"""
Debug script to test the payment process
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from apps.orders.models import Order
from apps.payments.views import PaymentProcessView
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

User = get_user_model()

def debug_payment_issue():
    print("=== Payment Debug Script ===")
    
    # Check settings
    print(f"STRIPE_PUBLISHABLE_KEY: {getattr(settings, 'STRIPE_PUBLISHABLE_KEY', 'NOT SET')}")
    print(f"STRIPE_SECRET_KEY: {'SET' if getattr(settings, 'STRIPE_SECRET_KEY', '') else 'NOT SET'}")
    
    # Check if there are any orders
    orders_count = Order.objects.count()
    print(f"Total orders in database: {orders_count}")
    
    if orders_count > 0:
        latest_order = Order.objects.latest('created_at')
        print(f"Latest order: {latest_order.id} - {latest_order.order_number}")
        print(f"Order user: {latest_order.user.email}")
        print(f"Order status: {latest_order.status}")
        print(f"Order total: ${latest_order.total}")
        
        # Create a mock request to test the view
        factory = RequestFactory()
        request = factory.get('/payments/process/')
        
        # Add session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add user
        request.user = latest_order.user
        
        # Test without order_id in session
        print("\n--- Test 1: No order_id in session ---")
        view = PaymentProcessView()
        view.request = request
        context = view.get_context_data()
        print(f"Order in context: {context.get('order', 'None')}")
        print(f"Stripe key in context: {context.get('stripe_public_key', 'None')}")
        
        # Test with order_id in session
        print("\n--- Test 2: With order_id in session ---")
        request.session['order_id'] = str(latest_order.id)
        context = view.get_context_data()
        print(f"Order in context: {context.get('order', 'None')}")
        print(f"Stripe key in context: {context.get('stripe_public_key', 'None')}")
        
    else:
        print("No orders found. Create an order first.")
    
    print("\n=== Debug Complete ===")

if __name__ == '__main__':
    debug_payment_issue()