from rest_framework import serializers
from ..models import Payment, PaymentRefund, PaymentMethod


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'amount', 'currency', 'status', 
            'status_display', 'payment_method', 'description', 'failure_reason',
            'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'processed_at']


class PaymentRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'payment', 'amount', 'currency', 'status', 'reason',
            'description', 'failure_reason', 'processed_by',
            'created_at', 'updated_at', 'processed_at'
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'method_type', 'card_brand', 'card_last4', 
            'card_exp_month', 'card_exp_year', 'is_default', 
            'display_name', 'created_at'
        ]
    
    def get_display_name(self, obj):
        return str(obj)


class CreatePaymentIntentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method_id = serializers.CharField(required=False, allow_blank=True)


class ConfirmPaymentSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField()
    payment_method_id = serializers.CharField(required=False, allow_blank=True)