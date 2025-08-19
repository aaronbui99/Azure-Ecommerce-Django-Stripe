"""
Management command to add images to products programmatically
Usage: python manage.py add_product_images
"""

from django.core.management.base import BaseCommand
from django.core.files import File
from apps.products.models import Product, ProductImage
import os


class Command(BaseCommand):
    help = 'Add images to products programmatically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product-id',
            type=int,
            help='ID of the product to add images to',
        )
        parser.add_argument(
            '--image-path',
            type=str,
            help='Path to the image file',
        )
        parser.add_argument(
            '--alt-text',
            type=str,
            default='',
            help='Alt text for the image',
        )
        parser.add_argument(
            '--is-primary',
            action='store_true',
            help='Set this image as primary',
        )

    def handle(self, *args, **options):
        product_id = options['product_id']
        image_path = options['image_path']
        alt_text = options['alt_text']
        is_primary = options['is_primary']

        if not product_id or not image_path:
            self.stdout.write(
                self.style.ERROR('Both --product-id and --image-path are required')
            )
            return

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Product with ID {product_id} does not exist')
            )
            return

        if not os.path.exists(image_path):
            self.stdout.write(
                self.style.ERROR(f'Image file {image_path} does not exist')
            )
            return

        # If setting as primary, remove primary flag from other images
        if is_primary:
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)

        # Create the ProductImage
        with open(image_path, 'rb') as img_file:
            django_file = File(img_file)
            product_image = ProductImage.objects.create(
                product=product,
                alt_text=alt_text or product.name,
                is_primary=is_primary,
                sort_order=ProductImage.objects.filter(product=product).count()
            )
            product_image.image.save(
                os.path.basename(image_path),
                django_file,
                save=True
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added image to product "{product.name}" '
                f'(Primary: {is_primary})'
            )
        )

        # Example usage instructions
        self.stdout.write('\n' + '='*50)
        self.stdout.write('EXAMPLE USAGE:')
        self.stdout.write('python manage.py add_product_images --product-id 1 --image-path "/path/to/image.jpg" --alt-text "Product front view" --is-primary')
        self.stdout.write('='*50)