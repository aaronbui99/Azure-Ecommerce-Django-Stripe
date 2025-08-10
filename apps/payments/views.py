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
from .models import Payment, PaymentWebhookEvent, PaymentMethod

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
                context['stripe_public_key'] = settings.STRIPE_PUBLISHABLE_KEY
                
                # Get user's saved payment methods
                context['payment_methods'] = PaymentMethod.objects.filter(
                    user=self.request.user,
                    is_active=True
                )
                
            except Order.DoesNotExist:
                pass
        
        return context


class CreatePaymentIntentView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
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


class AddPaymentMethodView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            
            if not payment_method_id:
                return JsonResponse({'error': 'Payment method ID required'}, status=400)
            
            # Retrieve payment method from Stripe
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Attach to customer (create customer if doesn't exist)
            if not hasattr(request.user, 'stripe_customer_id'):
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.get_full_name()
                )
                # Save customer ID to user model
                # You'd need to add this field to your User model
                # request.user.stripe_customer_id = customer.id
                # request.user.save()
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=getattr(request.user, 'stripe_customer_id', None)
            )
            
            # Save payment method
            payment_method = PaymentMethod.objects.create(
                user=request.user,
                stripe_payment_method_id=payment_method_id,
                method_type='card',  # Assuming card for now
                card_brand=pm.card.brand if pm.card else '',
                card_last4=pm.card.last4 if pm.card else '',
                card_exp_month=pm.card.exp_month if pm.card else None,
                card_exp_year=pm.card.exp_year if pm.card else None,
                is_default=not PaymentMethod.objects.filter(user=request.user).exists()
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