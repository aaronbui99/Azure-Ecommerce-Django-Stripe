from rest_framework import serializers
from ..models import Product, Category, ProductImage, Review


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 'short_description',
            'price', 'compare_price', 'sku', 'in_stock', 'is_on_sale', 
            'discount_percentage', 'images', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductDetailSerializer(ProductSerializer):
    reviews = serializers.SerializerMethodField()
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews']
    
    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_approved=True)[:5]  # Latest 5 reviews
        return ReviewSerializer(reviews, many=True).data


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'rating', 'title', 'content', 'user_name', 'is_verified_purchase', 'created_at']