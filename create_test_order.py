#!/usr/bin/env python
"""
Create a test order for testing payment flow
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_data():
    print("Creating test data...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    if created:
        user.set_password('testpassword123')
        user.save()
        print(f"Created test user: {user.email}")
    else:
        print(f"Using existing user: {user.email}")
    
    # Create test category
    category, created = Category.objects.get_or_create(
        name='Test Category',
        defaults={
            'slug': 'test-category',
            'description': 'Test category for payment testing'
        }
    )
    
    # Create test products
    products_data = [
        {
            'name': 'Test Product 1',
            'slug': 'test-product-1',
            'description': 'A test product for payment testing',
            'price': Decimal('29.99'),
            'sku': 'TEST-001'
        },
        {
            'name': 'Premium Test Product',
            'slug': 'premium-test-product',
            'description': 'A premium test product',
            'price': Decimal('99.99'),
            'sku': 'TEST-002'
        }
    ]
    
    products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults={
                **product_data,
                'category': category,
                'is_active': True,
                'stock_quantity': 100
            }
        )
        products.append(product)
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Using existing product: {product.name}")
    
    # Create test order
    order = Order.objects.create(
        user=user,
        email=user.email,
        # Billing address
        billing_first_name='Test',
        billing_last_name='User',
        billing_address_1='123 Test Street',
        billing_city='Test City',
        billing_state='Test State',
        billing_postal_code='12345',
        billing_country='United States',
        billing_phone='555-123-4567',
        # Shipping address
        shipping_first_name='Test',
        shipping_last_name='User',
        shipping_address_1='123 Test Street',
        shipping_city='Test City',
        shipping_state='Test State',
        shipping_postal_code='12345',
        shipping_country='United States',
        shipping_phone='555-123-4567',
        # Totals
        subtotal=Decimal('129.98'),
        total=Decimal('129.98'),
        status='pending'
    )
    
    # Create order items
    OrderItem.objects.create(
        order=order,
        product=products[0],
        product_name=products[0].name,
        product_sku=products[0].sku,
        unit_price=products[0].price,
        quantity=2
    )
    
    OrderItem.objects.create(
        order=order,
        product=products[1],
        product_name=products[1].name,
        product_sku=products[1].sku,
        unit_price=products[1].price,
        quantity=1
    )
    
    print(f"\nCreated test order: {order.order_number}")
    print(f"Order ID: {order.id}")
    print(f"Order total: ${order.total}")
    print(f"Order user: {order.user.email}")
    print(f"Order items: {order.items.count()}")
    
    print(f"\nTo test payment:")
    print(f"1. Login with email: {user.email} and password: testpassword123")
    print(f"2. Visit /payments/process/ after setting session with order_id: {order.id}")
    print(f"3. Or run the following in Django shell:")
    print(f"   request.session['order_id'] = '{order.id}'")
    
    return order, user

if __name__ == '__main__':
    order, user = create_test_data()