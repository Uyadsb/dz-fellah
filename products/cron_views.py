import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from . import queries as product_queries


@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_anti_gaspi_cron(request):
    """
    Protected endpoint for Railway cron jobs.
    Applies anti-gaspi discounts to eligible products.
    """
    
    auth_header = request.headers.get('X-Cron-Secret')
    expected_secret = os.getenv('CRON_SECRET_TOKEN', 'dz-fellah-secret-2025-anti-gaspi')
    
    if auth_header != expected_secret:
        return JsonResponse({
            'error': 'Unauthorized - Invalid cron secret'
        }, status=403)
    
    try:
        
        count = product_queries.mark_products_as_anti_gaspi()
        
        return JsonResponse({
            'success': True,
            'message': f'Anti-gaspi applied successfully',
            'products_updated': count
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e) 
        }, status=500) 
