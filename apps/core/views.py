from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db import connection


class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Azure E-commerce Platform'
        return context


def health_check(request):
    """Health check endpoint for Azure App Service and Front Door"""
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)