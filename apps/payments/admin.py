from django.contrib import admin
from .models import Payment, PaymentRefund, PaymentWebhookEvent, PaymentMethod


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'user', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['id', 'order__order_number', 'user__email', 'stripe_payment_intent_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'order', 'user', 'amount', 'currency', 'status', 'payment_method')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_payment_method_id', 'stripe_charge_id')
        }),
        ('Additional Information', {
            'fields': ('description', 'failure_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'status', 'reason', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['id', 'payment__id', 'stripe_refund_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']


@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = ['stripe_event_id', 'event_type', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'method_type', 'card_brand', 'card_last4', 'is_default', 'is_active']
    list_filter = ['method_type', 'card_brand', 'is_default', 'is_active', 'created_at']
    search_fields = ['user__email', 'stripe_payment_method_id', 'card_last4']