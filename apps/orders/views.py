from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, View
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from .models import Order, Cart, CartItem, OrderItem
from apps.products.models import Product, ProductVariant
import json


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            'items__product',
            'status_history'
        )


class CartView(TemplateView):
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart()
        context['cart'] = cart
        return context
    
    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart


class AddToCartView(View):
    def post(self, request):
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            product_id = data.get('product_id')
            variant_id = data.get('variant_id')
            quantity = int(data.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id, is_active=True)
            variant = None
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
            
            # Get or create cart
            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                cart, created = Cart.objects.get_or_create(session_key=session_key)
            
            # Get current price
            price = product.price
            if variant:
                price += variant.price_adjustment
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={'quantity': quantity, 'price': price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Return JSON for AJAX requests, redirect for form submissions
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f'{product.name} added to cart',
                    'cart_total': cart.total_items
                })
            else:
                messages.success(request, f'{product.name} added to cart')
                return redirect('orders:cart')
            
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                }, status=400)
            else:
                messages.error(request, f'Error adding to cart: {str(e)}')
                return redirect('products:list')


class UpdateCartView(View):
    def post(self, request):
        try:
            # Handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
                
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))
            
            # Get cart
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
            else:
                session_key = request.session.session_key
                cart = get_object_or_404(Cart, session_key=session_key)
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            
            if quantity <= 0:
                cart_item.delete()
                message = 'Item removed from cart'
            else:
                cart_item.quantity = quantity
                cart_item.save()
                message = 'Cart updated'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total': cart.total_items,
                'subtotal': float(cart.subtotal)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


class RemoveFromCartView(View):
    def post(self, request, item_id):
        try:
            # Get cart
            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
            else:
                session_key = request.session.session_key
                cart = get_object_or_404(Cart, session_key=session_key)
            
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            product_name = cart_item.product.name
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from cart',
                'cart_total': cart.total_items
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=self.request.user)
            context['cart'] = cart
        except Cart.DoesNotExist:
            context['cart'] = None
        
        return context
    
    def post(self, request):
        try:
            with transaction.atomic():
                # Get user's cart
                cart = get_object_or_404(Cart, user=request.user)
                
                if not cart.items.exists():
                    messages.error(request, 'Your cart is empty.')
                    return redirect('orders:cart')
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    billing_first_name=request.POST.get('billing_first_name'),
                    billing_last_name=request.POST.get('billing_last_name'),
                    billing_address_1=request.POST.get('billing_address_1'),
                    billing_address_2=request.POST.get('billing_address_2', ''),
                    billing_city=request.POST.get('billing_city'),
                    billing_state=request.POST.get('billing_state'),
                    billing_postal_code=request.POST.get('billing_postal_code'),
                    billing_country=request.POST.get('billing_country'),
                    billing_phone=request.POST.get('billing_phone', ''),
                    shipping_first_name=request.POST.get('shipping_first_name'),
                    shipping_last_name=request.POST.get('shipping_last_name'),
                    shipping_address_1=request.POST.get('shipping_address_1'),
                    shipping_address_2=request.POST.get('shipping_address_2', ''),
                    shipping_city=request.POST.get('shipping_city'),
                    shipping_state=request.POST.get('shipping_state'),
                    shipping_postal_code=request.POST.get('shipping_postal_code'),
                    shipping_country=request.POST.get('shipping_country'),
                    shipping_phone=request.POST.get('shipping_phone', ''),
                    subtotal=cart.subtotal,
                    total=cart.subtotal  # Simplified - add tax/shipping logic
                )
                
                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=cart_item.variant,
                        product_name=cart_item.product.name,
                        product_sku=cart_item.product.sku,
                        unit_price=cart_item.price,
                        quantity=cart_item.quantity
                    )
                
                # Clear cart
                cart.items.all().delete()
                
                # Redirect to payment
                request.session['order_id'] = str(order.id)
                return redirect('payments:process')
                
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            return redirect('orders:checkout')


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=self.request.user)
                context['order'] = order
                # Clear order_id from session
                del self.request.session['order_id']
            except Order.DoesNotExist:
                pass
        return context