from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, Cart, CartItem, ShippingMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'email', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__email', 'email']
    readonly_fields = ['id', 'order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'order_number', 'user', 'email', 'status', 'notes')
        }),
        ('Billing Address', {
            'fields': ('billing_first_name', 'billing_last_name', 'billing_address_1', 
                      'billing_address_2', 'billing_city', 'billing_state', 
                      'billing_postal_code', 'billing_country', 'billing_phone')
        }),
        ('Shipping Address', {
            'fields': ('shipping_first_name', 'shipping_last_name', 'shipping_address_1',
                      'shipping_address_2', 'shipping_city', 'shipping_state',
                      'shipping_postal_code', 'shipping_country', 'shipping_phone')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total')
        }),
        ('Fulfillment', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'session_key']
    inlines = [CartItemInline]


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'estimated_days', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']