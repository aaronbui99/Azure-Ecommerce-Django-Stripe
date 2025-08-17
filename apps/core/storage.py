"""
Custom Azure Storage backend that uses SAS tokens for private containers
"""

from storages.backends.azure_storage import AzureStorage
from django.conf import settings
import environ
from urllib.parse import urlencode

# Initialize environment and read .env file
env = environ.Env()
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(BASE_DIR / '.env')


class AzureMediaStorage(AzureStorage):
    """
    Custom Azure Storage backend that generates SAS token URLs
    for private containers that don't allow public access
    """
    
    def url(self, name):
        """
        Override URL generation to use SAS token URLs for private Azure Storage
        """
        # Get SAS token from environment
        sas_token = env('AZURE_BLOB_SAS_TOKEN', default='')
        
        if sas_token:
            # Generate URL with SAS token
            base_url = f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER}/{name}"
            return f"{base_url}?{sas_token}"
        else:
            # Fall back to default behavior
            return super().url(name)