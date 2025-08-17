from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe_card', 'Credit/Debit Card'),
        ('stripe_bank', 'Bank Transfer'),
        ('stripe_wallet', 'Digital Wallet'),
    ]
    
    # Payment identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Related models
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    
    # Payment metadata
    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.order.order_number} (${self.amount})"
    
    @property
    def is_successful(self):
        return self.status == 'succeeded'
    
    @property
    def can_be_refunded(self):
        return self.status in ['succeeded'] and not self.refunds.filter(status='succeeded').exists()


class PaymentRefund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    REFUND_REASON_CHOICES = [
        ('duplicate', 'Duplicate'),
        ('fraudulent', 'Fraudulent'),
        ('requested_by_customer', 'Requested by customer'),
        ('expired_uncaptured_charge', 'Expired uncaptured charge'),
        ('other', 'Other'),
    ]
    
    # Refund identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Related payment
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.CharField(max_length=30, choices=REFUND_REASON_CHOICES, default='requested_by_customer')
    
    # Stripe integration
    stripe_refund_id = models.CharField(max_length=255, unique=True)
    
    # Refund metadata
    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Admin details
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.id} - ${self.amount}"


class PaymentWebhookEvent(models.Model):
    """Store Stripe webhook events for processing"""
    EVENT_TYPES = [
        ('payment_intent.succeeded', 'Payment Intent Succeeded'),
        ('payment_intent.payment_failed', 'Payment Intent Failed'),
        ('payment_intent.canceled', 'Payment Intent Canceled'),
        ('charge.dispute.created', 'Charge Dispute Created'),
        ('invoice.payment_succeeded', 'Invoice Payment Succeeded'),
        ('invoice.payment_failed', 'Invoice Payment Failed'),
    ]
    
    # Event identification
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    
    # Event data
    data = models.JSONField()
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    # Related payment (if applicable)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True, related_name='webhook_events')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook Event {self.stripe_event_id} - {self.event_type}"


class StripeCustomer(models.Model):
    """Store Stripe customer information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stripe Customer {self.stripe_customer_id} for {self.user.email}"


class PaymentMethod(models.Model):
    """Saved payment methods for users"""
    METHOD_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('wallet', 'Digital Wallet'),
    ]
    
    # User and identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    
    # Payment method details
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    
    # Card details (if applicable)
    card_brand = models.CharField(max_length=20, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # Settings
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.method_type == 'card':
            return f"{self.card_brand} ending in {self.card_last4}"
        return f"{self.get_method_type_display()}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, remove default from other payment methods
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)