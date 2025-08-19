"""
Management command to set up Azure Storage containers
Usage: python manage.py setup_azure_storage
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from azure.storage.blob import BlobServiceClient, PublicAccess
from azure.core.exceptions import ResourceExistsError
import os
import environ
from pathlib import Path

# Initialize environment and read .env file
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
environ.Env.read_env(BASE_DIR / '.env')


class Command(BaseCommand):
    help = 'Set up Azure Storage containers for the application'

    def handle(self, *args, **options):
        if not env.bool('USE_AZURE_STORAGE', default=False):
            self.stdout.write(
                self.style.WARNING('Azure Storage is disabled. Enable it by setting USE_AZURE_STORAGE=True in .env file')
            )
            return

        # Get Azure credentials from environment
        account_name = env('AZURE_ACCOUNT_NAME', default='')
        account_key = env('AZURE_BLOB_KEY', default='')
        container_name = env('AZURE_CONTAINER', default='media')

        if not account_name or not account_key:
            self.stdout.write(
                self.style.ERROR('Azure credentials not found. Please check AZURE_ACCOUNT_NAME and AZURE_BLOB_KEY in .env file')
            )
            return

        try:
            # Create BlobServiceClient
            blob_service_client = BlobServiceClient(
                account_url=f"https://{account_name}.blob.core.windows.net",
                credential=account_key
            )

            self.stdout.write(f"Connecting to Azure Storage account: {account_name}")

            # Test connection
            try:
                account_info = blob_service_client.get_account_information()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Successfully connected to Azure Storage account")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to connect to Azure Storage: {e}")
                )
                return

            # Create the media container
            try:
                container_client = blob_service_client.create_container(
                    name=container_name,
                    public_access=PublicAccess.Blob  # Allow public read access to blobs
                )
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created container '{container_name}' with public blob access")
                )
            except ResourceExistsError:
                self.stdout.write(
                    self.style.WARNING(f"Container '{container_name}' already exists")
                )
                container_client = blob_service_client.get_container_client(container_name)
                
                # Try to update access policy (may fail if storage account doesn't allow public access)
                try:
                    container_client.set_container_access_policy(
                        signed_identifiers={},
                        public_access=PublicAccess.Blob
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Updated container '{container_name}' access policy")
                    )
                except Exception as access_error:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Could not set public access (this is okay for production): {access_error}")
                    )
                    self.stdout.write(
                        "Container will use private access - Django will handle authentication"
                    )
            except Exception as create_error:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to create container: {create_error}")
                )
                return

            # Get container client for further operations
            container_client = blob_service_client.get_container_client(container_name)

            # Create subdirectories (virtual folders) for organization
            subdirectories = ['products/', 'categories/', 'users/']
            
            for subdir in subdirectories:
                try:
                    # Create a placeholder blob to establish the "directory"
                    blob_client = container_client.get_blob_client(f"{subdir}.gitkeep")
                    blob_client.upload_blob(
                        data="# This file creates the directory structure in Azure Blob Storage\n",
                        overwrite=True
                    )
                    self.stdout.write(f"  ✓ Created directory: {subdir}")
                except Exception as e:
                    self.stdout.write(f"  ⚠ Directory {subdir}: {e}")

            # Test upload/download functionality
            try:
                test_blob_name = "test-connection.txt"
                test_content = "Azure Blob Storage connection test - this file can be safely deleted"
                
                blob_client = container_client.get_blob_client(test_blob_name)
                
                # Upload test file
                blob_client.upload_blob(data=test_content, overwrite=True)
                
                # Download test file to verify
                downloaded_content = blob_client.download_blob().readall().decode('utf-8')
                
                if downloaded_content == test_content:
                    self.stdout.write(
                        self.style.SUCCESS("✓ Upload/download test successful")
                    )
                    
                    # Clean up test file
                    blob_client.delete_blob()
                    self.stdout.write("✓ Cleaned up test file")
                else:
                    self.stdout.write(
                        self.style.ERROR("✗ Upload/download test failed - content mismatch")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Upload/download test failed: {e}")
                )

            # Display configuration summary
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.SUCCESS("AZURE STORAGE SETUP COMPLETE"))
            self.stdout.write("="*60)
            self.stdout.write(f"Account Name: {account_name}")
            self.stdout.write(f"Container: {container_name}")
            self.stdout.write(f"Access Level: Public (blob)")
            self.stdout.write(f"Media URL: https://{account_name}.blob.core.windows.net/{container_name}/")
            self.stdout.write("\nYou can now:")
            self.stdout.write("1. Upload product images via Django admin")
            self.stdout.write("2. Access uploaded files via their blob URLs")
            self.stdout.write("3. Use the Azure Storage Explorer to manage files")
            self.stdout.write("="*60)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to set up Azure Storage: {e}")
            )
            self.stdout.write("\nTroubleshooting:")
            self.stdout.write("1. Verify AZURE_ACCOUNT_NAME and AZURE_BLOB_KEY in .env")
            self.stdout.write("2. Check Azure Storage account exists and is accessible")
            self.stdout.write("3. Ensure storage account key is correct and active")