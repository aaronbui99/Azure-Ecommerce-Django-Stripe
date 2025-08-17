from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.generic import TemplateView
from azure.storage.blob import BlobServiceClient
import mimetypes
import os
import environ

# Initialize environment and read .env file
env = environ.Env()
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(BASE_DIR / '.env')


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'core/home.html'


def health_check(request):
    """Health check endpoint"""
    return HttpResponse("OK", content_type="text/plain")


def serve_azure_media(request, path):
    """
    Serve media files from Azure Blob Storage with authentication
    This handles private storage containers
    """
    if not env.bool('USE_AZURE_STORAGE', default=False):
        raise Http404("Azure Storage not configured")
    
    try:
        # Get Azure credentials
        account_name = env('AZURE_ACCOUNT_NAME')
        account_key = env('AZURE_BLOB_KEY') 
        container_name = env('AZURE_CONTAINER', default='media')
        
        # Create blob service client
        blob_service_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=account_key
        )
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=path
        )
        
        # Download blob content
        blob_data = blob_client.download_blob()
        content = blob_data.readall()
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Create response
        response = HttpResponse(content, content_type=content_type)
        
        # Set cache headers for better performance
        response['Cache-Control'] = 'public, max-age=3600'  # 1 hour cache
        
        return response
        
    except Exception as e:
        print(f"Error serving media file {path}: {e}")
        raise Http404("File not found")