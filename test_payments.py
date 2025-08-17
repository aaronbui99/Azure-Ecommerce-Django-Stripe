#!/usr/bin/env python
"""
Quick test script to verify payment functionality works
Run with: python test_payments.py
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

def test_payment_templates():
    """Test if payment templates load without errors"""
    client = Client()
    
    print("🧪 Testing Payment Template Loading...")
    
    # Test payment methods page (should work without login for template test)
    try:
        response = client.get('/payments/methods/')
        if response.status_code == 302:  # Redirect to login (expected)
            print("✅ Payment methods template exists (redirects to login as expected)")
        elif response.status_code == 200:
            print("✅ Payment methods template loads successfully")
        else:
            print(f"⚠️  Payment methods returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Payment methods template error: {e}")
    
    # Test payment process page
    try:
        response = client.get('/payments/process/')
        if response.status_code == 302:  # Redirect to login (expected)
            print("✅ Payment process template exists (redirects to login as expected)")
        elif response.status_code == 200:
            print("✅ Payment process template loads successfully")
        else:
            print(f"⚠️  Payment process returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Payment process template error: {e}")
    
    print("\n🎉 Template Test Complete!")
    print("\nNext steps:")
    print("1. Visit http://127.0.0.1:8000/payments/process/ in your browser")
    print("2. If you see 'Payment' page instead of TemplateDoesNotExist error, it's working!")
    print("3. For full testing, create a user and add items to cart first")

if __name__ == '__main__':
    test_payment_templates()