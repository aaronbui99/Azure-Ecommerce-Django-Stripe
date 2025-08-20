import json
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from apps.orders.models import Order
from .models import Payment, PaymentWebhookEvent, PaymentMethod, StripeCustomer

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentProcessView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/process.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get order from session
        order_id = self.request.session.get('order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=self.request.user)
                context['order'] = order
                
            except Order.DoesNotExist:
                context['order'] = None
        else:
            context['order'] = None
        
        # Always include stripe_public_key
        context['stripe_public_key'] = settings.STRIPE_PUBLISHABLE_KEY
        
        # Get user's saved payment methods
        context['payment_methods'] = PaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        )
        
        return context


class CreatePaymentIntentView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body) if request.body else {}
            else:
                data = request.POST
                
            order_id = request.session.get('order_id')
            
            if not order_id:
                return JsonResponse({'error': 'No order found'}, status=400)
            
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'order_id': str(order.id),
                    'user_id': str(request.user.id),
                },
                description=f'Order {order.order_number}'
            )
            
            # Create Payment record
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.total,
                stripe_payment_intent_id=intent.id,
                payment_method='stripe_card',
                description=f'Payment for order {order.order_number}'
            )
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'payment_id': str(payment.id)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class PaymentConfirmView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')
            
            if not payment_intent_id:
                return JsonResponse({'error': 'Payment intent ID required'}, status=400)
            
            # Get payment record
            payment = get_object_or_404(
                Payment, 
                stripe_payment_intent_id=payment_intent_id,
                user=request.user
            )
            
            # Retrieve PaymentIntent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                payment.status = 'succeeded'
                payment.stripe_charge_id = intent.charges.data[0].id if intent.charges.data else ''
                payment.save()
                
                # Update order status
                order = payment.order
                order.status = 'confirmed'
                order.save()
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('orders:success')
                })
            else:
                payment.status = 'failed'
                payment.failure_reason = intent.last_payment_error.message if intent.last_payment_error else 'Unknown error'
                payment.save()
                
                return JsonResponse({
                    'success': False,
                    'error': 'Payment failed'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
        # Store webhook event
        webhook_event, created = PaymentWebhookEvent.objects.get_or_create(
            stripe_event_id=event['id'],
            defaults={
                'event_type': event['type'],
                'data': event['data']
            }
        )
        
        if created:
            # Process the event
            self.handle_webhook_event(webhook_event)
        
        return HttpResponse(status=200)
    
    def handle_webhook_event(self, webhook_event):
        """Process webhook event"""
        try:
            event_type = webhook_event.event_type
            
            if event_type == 'payment_intent.succeeded':
                self.handle_payment_succeeded(webhook_event)
            elif event_type == 'payment_intent.payment_failed':
                self.handle_payment_failed(webhook_event)
            elif event_type == 'payment_intent.canceled':
                self.handle_payment_canceled(webhook_event)
            
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
        except Exception as e:
            webhook_event.processing_error = str(e)
            webhook_event.save()
    
    def handle_payment_succeeded(self, webhook_event):
        """Handle successful payment"""
        payment_intent = webhook_event.data['object']
        
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'succeeded'
            payment.save()
            
            # Update order
            order = payment.order
            order.status = 'confirmed'
            order.save()
            
        except Payment.DoesNotExist:
            pass
    
    def handle_payment_failed(self, webhook_event):
        """Handle failed payment"""
        payment_intent = webhook_event.data['object']
        
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'failed'
            payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
            payment.save()
            
        except Payment.DoesNotExist:
            pass
    
    def handle_payment_canceled(self, webhook_event):
        """Handle canceled payment"""
        payment_intent = webhook_event.data['object']
        
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            payment.status = 'cancelled'
            payment.save()
            
        except Payment.DoesNotExist:
            pass


class PaymentMethodListView(LoginRequiredMixin, ListView):
    model = PaymentMethod
    template_name = 'payments/methods.html'
    context_object_name = 'payment_methods'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


class AddPaymentMethodView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            set_as_default = data.get('set_as_default', False)
            
            if not payment_method_id:
                return JsonResponse({'error': 'Payment method ID required'}, status=400)
            
            # Retrieve payment method from Stripe
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Get or create Stripe customer
            stripe_customer, created = StripeCustomer.objects.get_or_create(
                user=request.user,
                defaults={
                    'stripe_customer_id': ''  # Will be set below
                }
            )
            
            if created or not stripe_customer.stripe_customer_id:
                # Create Stripe customer
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.get_full_name(),
                    metadata={
                        'user_id': str(request.user.id)
                    }
                )
                stripe_customer.stripe_customer_id = customer.id
                stripe_customer.save()
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer.stripe_customer_id
            )
            
            # Determine if this should be the default
            existing_methods_count = PaymentMethod.objects.filter(user=request.user, is_active=True).count()
            is_default = set_as_default or existing_methods_count == 0
            
            # If setting as default, remove default from other methods
            if is_default:
                PaymentMethod.objects.filter(user=request.user, is_active=True).update(is_default=False)
            
            # Save payment method
            payment_method = PaymentMethod.objects.create(
                user=request.user,
                stripe_payment_method_id=payment_method_id,
                method_type='card',  # Assuming card for now
                card_brand=pm.card.brand if pm.card else '',
                card_last4=pm.card.last4 if pm.card else '',
                card_exp_month=pm.card.exp_month if pm.card else None,
                card_exp_year=pm.card.exp_year if pm.card else None,
                is_default=is_default
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Payment method added successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class DeletePaymentMethodView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            payment_method = get_object_or_404(
                PaymentMethod,
                pk=pk,
                user=request.user,
                is_active=True
            )
            
            # Detach from Stripe
            stripe.PaymentMethod.detach(payment_method.stripe_payment_method_id)
            
            # Mark as inactive
            payment_method.is_active = False
            payment_method.save()
            
            messages.success(request, 'Payment method removed successfully')
            return redirect('payments:methods')
            
        except Exception as e:
            messages.error(request, f'Error removing payment method: {str(e)}')
            return redirect('payments:methods')


class SetDefaultPaymentMethodView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            # Get the payment method to set as default
            payment_method = get_object_or_404(
                PaymentMethod,
                pk=pk,
                user=request.user,
                is_active=True
            )
            
            # Remove default from all other payment methods
            PaymentMethod.objects.filter(user=request.user, is_active=True).update(is_default=False)
            
            # Set this payment method as default
            payment_method.is_default = True
            payment_method.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Payment method set as default successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class ProcessSavedPaymentMethodView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            # Parse request data
            try:
                data = json.loads(request.body.decode('utf-8')) if request.body else {}
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
            payment_method_id = data.get('payment_method_id')
            
            if not payment_method_id:
                return JsonResponse({'error': 'Payment method ID is required'}, status=400)
            
            # Convert to integer if it's a string
            try:
                payment_method_id = int(payment_method_id)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid payment method ID format'}, status=400)
            
            
            # Get order from session
            order_id = request.session.get('order_id')
            if not order_id:
                # Check if we can get it from the user's most recent pending order
                try:
                    order = Order.objects.filter(
                        user=request.user,
                        status__in=['pending', 'processing']
                    ).latest('created_at')
                    # Store in session for future use
                    request.session['order_id'] = order.id
                    order_id = order.id
                except Order.DoesNotExist:
                    return JsonResponse({'error': 'No order found. Please complete checkout first.'}, status=400)
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found or access denied'}, status=400)
            
            # Get the saved payment method
            try:
                payment_method = PaymentMethod.objects.get(
                    id=payment_method_id,
                    user=request.user,
                    is_active=True
                )
            except PaymentMethod.DoesNotExist:
                available_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
                return JsonResponse({'error': 'Payment method not found or access denied'}, status=400)
            
            # Get Stripe customer
            try:
                stripe_customer = StripeCustomer.objects.get(user=request.user)
            except StripeCustomer.DoesNotExist:
                return JsonResponse({'error': 'Stripe customer not found. Please add a payment method first.'}, status=400)
            
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total * 100),  # Convert to cents
                    currency='usd',
                    customer=stripe_customer.stripe_customer_id,
                    payment_method=payment_method.stripe_payment_method_id,
                    confirmation_method='manual',
                    confirm=True,
                    return_url=request.build_absolute_uri(reverse('orders:success')),
                    metadata={
                        'order_id': str(order.id),
                        'user_id': str(request.user.id),
                    },
                    expand=['latest_charge']  # Expand the latest charge to get charge details
                )
            except stripe.error.StripeError as e:
                return JsonResponse({'error': f'Stripe error: {str(e)}'}, status=400)
            
            # Create Payment record
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.total,
                stripe_payment_intent_id=intent.id,
                payment_method='stripe_card',  # Use existing choice instead of 'stripe_saved_card'
                stripe_payment_method_id=payment_method.stripe_payment_method_id,
                description=f'Payment for order {order.order_number} (saved card ending in {payment_method.card_last4})'
            )
            
            # Handle the payment intent status
            if intent.status == 'succeeded':
                payment.status = 'succeeded'
                # Use latest_charge since we expanded it in the PaymentIntent creation
                payment.stripe_charge_id = intent.latest_charge.id if intent.latest_charge else ''
                payment.save()
                
                # Update order status
                order.status = 'confirmed'
                order.save()
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('orders:success')
                })
            elif intent.status == 'requires_action':
                return JsonResponse({
                    'requires_action': True,
                    'payment_intent_client_secret': intent.client_secret
                })
            else:
                payment.status = 'failed'
                payment.failure_reason = intent.last_payment_error.message if intent.last_payment_error else 'Payment failed'
                payment.save()
                
                return JsonResponse({
                    'success': False,
                    'error': intent.last_payment_error.message if intent.last_payment_error else 'Payment failed'
                })
                
        except stripe.error.CardError as e:
            return JsonResponse({'error': e.user_message}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class CreateTestOrderView(LoginRequiredMixin, View):
    """Create a test order for payment testing (only available in DEBUG mode)"""
    
    def get(self, request):
        if not settings.DEBUG:
            return redirect('core:home')
        
        try:
            from decimal import Decimal
            from apps.products.models import Product, Category
            
            # Create test category and products if they don't exist
            category, created = Category.objects.get_or_create(
                name='Test Category',
                defaults={
                    'slug': 'test-category',
                    'description': 'Test category for payment testing'
                }
            )
            
            product, created = Product.objects.get_or_create(
                sku='TEST-001',
                defaults={
                    'name': 'Test Product for Payment',
                    'slug': 'test-product-payment',
                    'description': 'A test product for payment testing',
                    'price': Decimal('29.99'),
                    'category': category,
                    'is_active': True,
                    'inventory_quantity': 100
                }
            )
            
            # Create test order
            from apps.orders.models import Order, OrderItem
            
            order = Order.objects.create(
                user=request.user,
                email=request.user.email,
                billing_first_name=request.user.first_name or 'Test',
                billing_last_name=request.user.last_name or 'User',
                billing_address_1='123 Test Street',
                billing_city='Test City',
                billing_state='Test State',
                billing_postal_code='12345',
                billing_country='United States',
                billing_phone='555-123-4567',
                shipping_first_name=request.user.first_name or 'Test',
                shipping_last_name=request.user.last_name or 'User',
                shipping_address_1='123 Test Street',
                shipping_city='Test City',
                shipping_state='Test State',
                shipping_postal_code='12345',
                shipping_country='United States',
                shipping_phone='555-123-4567',
                subtotal=product.price,
                total=product.price,
                status='pending'
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                unit_price=product.price,
                quantity=1
            )
            
            # Set order in session
            request.session['order_id'] = str(order.id)
            
            messages.success(request, f'Test order created: {order.order_number}')
            return redirect('payments:process')
            
        except Exception as e:
            messages.error(request, f'Error creating test order: {str(e)}')
            return redirect('core:home')