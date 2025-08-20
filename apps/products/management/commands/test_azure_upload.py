"""
Management command to test Azure Storage image upload
Usage: python manage.py test_azure_upload
"""

import tempfile
import os
from PIL import Image
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.products.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = 'Test Azure Storage image upload functionality'

    def handle(self, *args, **options):
        """Test creating a product with an image uploaded to Azure Storage"""
        
        self.stdout.write("Testing Azure Storage image upload...")
        
        # Create a test category
        category, created = Category.objects.get_or_create(
            name="Test Electronics",
            defaults={'description': 'Test category for Azure upload test'}
        )
        self.stdout.write(f"Category: {category.name} ({'created' if created else 'exists'})")
        
        # Create a test product
        product, created = Product.objects.get_or_create(
            sku="TEST-AZURE-001",
            defaults={
                'name': 'Test Azure Product',
                'category': category,
                'description': 'Test product for Azure Storage upload verification',
                'price': 99.99,
                'inventory_quantity': 10
            }
        )
        self.stdout.write(f"Product: {product.name} ({'created' if created else 'exists'})")
        
        # Create a simple test image in memory
        image = Image.new('RGB', (300, 300), color='red')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image.save(temp_file.name, 'PNG')
            temp_file_path = temp_file.name
        
        try:
            # Read the image file
            with open(temp_file_path, 'rb') as img_file:
                image_content = img_file.read()
            
            # Create ProductImage instance
            product_image = ProductImage.objects.create(
                product=product,
                alt_text="Test Azure Storage Image",
                is_primary=True,
                sort_order=0
            )
            
            # Upload the image
            product_image.image.save(
                'test_azure_image.png',
                ContentFile(image_content),
                save=True
            )
            
            self.stdout.write(
                self.style.SUCCESS("✓ Image uploaded successfully!")
            )
            self.stdout.write(f"✓ Image URL: {product_image.image.url}")
            self.stdout.write(f"✓ Image name: {product_image.image.name}")
            
            # Verify the image exists
            try:
                # Try to access the image size (this will download it from Azure)
                width, height = product_image.image.width, product_image.image.height
                self.stdout.write(f"✓ Image dimensions verified: {width}x{height}")
                self.stdout.write(
                    self.style.SUCCESS("✓ Azure Storage upload test SUCCESSFUL!")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error accessing uploaded image: {e}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error during upload: {e}")
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("Test complete! You can now:")
        self.stdout.write("1. Visit http://127.0.0.1:8000/admin/products/product/ to see the product")
        self.stdout.write("2. Visit http://127.0.0.1:8000/products/ to see the product list")
        self.stdout.write("3. Try uploading more images via Django admin")
        self.stdout.write("="*50)