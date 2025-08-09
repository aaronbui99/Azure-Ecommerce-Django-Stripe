from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Order, Cart, CartItem
from apps.products.models import Product, ProductVariant
from .serializers import OrderSerializer, CartSerializer, CartItemSerializer, AddToCartSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            variant_id = serializer.validated_data.get('variant_id')
            quantity = serializer.validated_data['quantity']
            
            product = get_object_or_404(Product, id=product_id, is_active=True)
            variant = None
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Calculate price
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
            
            return Response({
                'message': f'{product.name} added to cart',
                'cart_total': cart.total_items
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        """Update cart item quantity"""
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or quantity is None:
            return Response(
                {'error': 'item_id and quantity are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            if int(quantity) <= 0:
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            else:
                cart_item.quantity = int(quantity)
                cart_item.save()
                return Response({'message': 'Cart updated'})
                
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart"""
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'item_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            product_name = cart_item.product.name
            cart_item.delete()
            
            return Response({'message': f'{product_name} removed from cart'})
            
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({'message': 'Cart cleared'})
        except Cart.DoesNotExist:
            return Response({'message': 'Cart is already empty'})