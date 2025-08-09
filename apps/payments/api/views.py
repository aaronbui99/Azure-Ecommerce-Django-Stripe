import stripe
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.orders.models import Order
from ..models import Payment, PaymentMethod
from .serializers import (
    PaymentSerializer, PaymentMethodSerializer, 
    CreatePaymentIntentSerializer, ConfirmPaymentSerializer
)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('order')
    
    @action(detail=False, methods=['post'])
    def create_intent(self, request):
        """Create Stripe PaymentIntent"""
        serializer = CreatePaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            payment_method_id = serializer.validated_data.get('payment_method_id')
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                
                # Create PaymentIntent
                intent_data = {
                    'amount': int(order.total * 100),  # Convert to cents
                    'currency': 'usd',
                    'metadata': {
                        'order_id': str(order.id),
                        'user_id': str(request.user.id),
                    },
                    'description': f'Order {order.order_number}'
                }
                
                if payment_method_id:
                    intent_data['payment_method'] = payment_method_id
                    intent_data['confirmation_method'] = 'manual'
                    intent_data['confirm'] = True
                
                intent = stripe.PaymentIntent.create(**intent_data)
                
                # Create Payment record
                payment = Payment.objects.create(
                    order=order,
                    user=request.user,
                    amount=order.total,
                    stripe_payment_intent_id=intent.id,
                    stripe_payment_method_id=payment_method_id or '',
                    payment_method='stripe_card',
                    description=f'Payment for order {order.order_number}'
                )
                
                response_data = {
                    'client_secret': intent.client_secret,
                    'payment_id': str(payment.id),
                    'requires_action': intent.status == 'requires_action'
                }
                
                if intent.status == 'requires_action':
                    response_data['next_action'] = intent.next_action
                elif intent.status == 'succeeded':
                    payment.status = 'succeeded'
                    payment.save()
                    order.status = 'confirmed'
                    order.save()
                    response_data['payment_succeeded'] = True
                
                return Response(response_data)
                
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Order not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm payment after 3D Secure or other authentication"""
        serializer = ConfirmPaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment_intent_id = serializer.validated_data['payment_intent_id']
            
            try:
                # Get payment record
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent_id,
                    user=request.user
                )
                
                # Retrieve and confirm PaymentIntent
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                
                if intent.status == 'requires_confirmation':
                    intent = stripe.PaymentIntent.confirm(payment_intent_id)
                
                if intent.status == 'succeeded':
                    payment.status = 'succeeded'
                    payment.stripe_charge_id = intent.charges.data[0].id if intent.charges.data else ''
                    payment.save()
                    
                    # Update order
                    order = payment.order
                    order.status = 'confirmed'
                    order.save()
                    
                    return Response({
                        'payment_succeeded': True,
                        'payment': PaymentSerializer(payment).data
                    })
                
                elif intent.status == 'requires_action':
                    return Response({
                        'requires_action': True,
                        'next_action': intent.next_action
                    })
                
                else:
                    payment.status = 'failed'
                    payment.failure_reason = intent.last_payment_error.message if intent.last_payment_error else 'Payment failed'
                    payment.save()
                    
                    return Response(
                        {'error': 'Payment failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except Payment.DoesNotExist:
                return Response(
                    {'error': 'Payment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def payment_methods(self, request):
        """Get user's saved payment methods"""
        payment_methods = PaymentMethod.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data)