from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from users.authentication import CustomJWTAuthentication  # ✅ ADDED
from .queries_ratings import (
    check_user_purchased_product,
    check_user_owns_product,
    get_product_basic_info,
    insert_or_update_rating,
    get_user_rating_for_product,
    delete_user_rating,
    get_product_rating_summary,
    get_producer_rating_summary
)


# ================================
# RATING ENDPOINTS
# ================================

@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])  # ✅ ADDED
@permission_classes([IsAuthenticated])
def create_product_rating(request):
    """
    Create or update a product rating
    
    POST /api/products/rate/
    Body: {
        "product_id": 123,
        "rating": 5
    }
    """
    try:
        user_id = request.user.id
        product_id = request.data.get('product_id')
        rating = request.data.get('rating')
        
        # Validation
        if not product_id or not rating:
            return Response({
                'error': 'product_id and rating are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            return Response({
                'error': 'Rating must be between 1 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if product exists
        product = get_product_basic_info(product_id)
        if not product:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user is trying to rate their own product
        if check_user_owns_product(user_id, product_id):
            return Response({
                'error': 'You cannot rate your own products'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if user purchased this product
        if not check_user_purchased_product(user_id, product_id):
            return Response({
                'error': 'You can only rate products you have purchased'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Insert or update rating
        now = datetime.now()
        result = insert_or_update_rating(product_id, user_id, rating, now, now)
        
        return Response({
            'message': 'Rating submitted successfully',
            'rating': {
                'id': result['id'],
                'product_id': result['product_id'],
                'user_id': result['user_id'],
                'rating': result['rating'],
                'created_at': result['created_at'].isoformat() if result['created_at'] else None,
                'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to create rating: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_product_ratings(request, product_id):
    """
    Get rating summary for a product
    
    GET /api/products/{product_id}/ratings/
    """
    try:
        summary = get_product_rating_summary(product_id)
        
        if not summary:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'product_id': summary['product_id'],
            'product_name': summary['product_name'],
            'producer_id': summary['producer_id'],
            'total_ratings': summary['total_ratings'],
            'average_rating': float(summary['average_rating']),
            'star_distribution': {
                '5': summary['five_star_count'],
                '4': summary['four_star_count'],
                '3': summary['three_star_count'],
                '2': summary['two_star_count'],
                '1': summary['one_star_count']
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get ratings: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])  # ✅ ADDED
@permission_classes([IsAuthenticated])
def get_my_product_rating(request, product_id):
    """
    Get the current user's rating for a specific product
    
    GET /api/products/{product_id}/my-rating/
    """
    try:
        user_id = request.user.id
        
        # Get user's rating
        rating = get_user_rating_for_product(user_id, product_id)
        
        # Check if can rate (purchased product and doesn't own it)
        owns_product = check_user_owns_product(user_id, product_id)
        has_purchased = check_user_purchased_product(user_id, product_id)
        can_rate = has_purchased and not owns_product
        
        if rating:
            return Response({
                'rating': rating['rating'],
                'created_at': rating['created_at'].isoformat() if rating['created_at'] else None,
                'updated_at': rating['updated_at'].isoformat() if rating['updated_at'] else None,
                'can_rate': can_rate
            })
        else:
            return Response({
                'rating': None,
                'can_rate': can_rate
            })
            
    except Exception as e:
        return Response({
            'error': f'Failed to get rating: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([CustomJWTAuthentication])  # ✅ ADDED
@permission_classes([IsAuthenticated])
def delete_product_rating_view(request, product_id):
    """
    Delete user's rating for a product
    
    DELETE /api/products/{product_id}/rating/
    """
    try:
        user_id = request.user.id
        
        deleted = delete_user_rating(user_id, product_id)
        
        if not deleted:
            return Response({
                'error': 'Rating not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': 'Rating deleted successfully'
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to delete rating: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_producer_rating_view(request, producer_id):
    """
    Get rating summary for a producer (based on all their products)
    
    GET /api/products/producer/{producer_id}/rating/
    """
    try:
        summary = get_producer_rating_summary(producer_id)
        
        # If no summary found (producer has no ratings yet), return default values
        if not summary:
            return Response({
                'producer_id': int(producer_id),
                'producer_name': 'Unknown Producer',
                'total_products': 0,
                'total_ratings': 0,
                'average_rating': 0.0
            })
        
        return Response({
            'producer_id': summary['producer_id'],
            'producer_name': summary['producer_name'],
            'total_products': summary['total_products'],
            'total_ratings': summary['total_ratings'],
            'average_rating': float(summary['average_rating']) if summary['average_rating'] else 0.0
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to get producer rating: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])  # ✅ ADDED
@permission_classes([IsAuthenticated])
def debug_purchase_check(request, product_id):
    """
    DEBUG: Check if user purchased product
    
    GET /api/products/<product_id>/debug-purchase/
    """
    user_id = request.user.id
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check the query
        cursor.execute("""
            SELECT 
                o.id as order_id,
                o.order_number,
                o.status as order_status,
                o.client_id,
                so.id as sub_order_id,
                so.status as sub_order_status,
                oi.product_id,
                oi.product_name
            FROM sub_orders so
            INNER JOIN order_items oi ON so.id = oi.sub_order_id
            INNER JOIN orders o ON so.parent_order_id = o.id
            WHERE o.client_id = %s 
            AND oi.product_id = %s
        """, [user_id, product_id])
        
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    has_purchased = check_user_purchased_product(user_id, product_id)
    
    return Response({
        'user_id': user_id,
        'product_id': product_id,
        'has_purchased': has_purchased,
        'orders_found': results
    })