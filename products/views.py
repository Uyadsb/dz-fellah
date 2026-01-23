from rest_framework import status, viewsets
<<<<<<< HEAD
from rest_framework.decorators import action
=======
from rest_framework.decorators import action, permission_classes, authentication_classes
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import queries
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
<<<<<<< HEAD
    SeasonalBasketSerializer,
    ClientSubscriptionSerializer,
    ProducerInfoSerializer,
    BasketProductSerializer,
)
from users.authentication import CustomJWTAuthentication
from users.permissions import IsProducer
from .seasonal_utils import is_product_in_season
=======
    ProducerInfoSerializer
)
from users.authentication import CustomJWTAuthentication
from users.permissions import IsProducer
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b


class ProductViewSet(viewsets.ViewSet):
    """
    ViewSet for public product operations.
    No authentication required.
    """
    
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        GET /api/products/
<<<<<<< HEAD
        Homepage products list with filters and search.
        """
        # Get all filters
        product_type = request.query_params.get('product_type')
        is_anti_gaspi = request.query_params.get('is_anti_gaspi')
        is_anti_gaspi_bool = is_anti_gaspi.lower() == 'true' if is_anti_gaspi else None
        search = request.query_params.get('search')
        producer_search = request.query_params.get('producer_search')
=======
        Homepage products list with filters.
        """
        product_type = request.query_params.get('product_type')
        is_anti_gaspi = request.query_params.get('is_anti_gaspi')
        is_anti_gaspi_bool = is_anti_gaspi.lower() == 'true' if is_anti_gaspi else None
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
        
        limit = request.query_params.get('limit', 20)
        try:
            limit = int(limit)
        except:
            limit = 20
        
<<<<<<< HEAD
        # Use advanced search if search parameters provided
        if search or producer_search:
            products = queries.search_products_advanced(
                search=search,
                producer_search=producer_search,
                product_type=product_type,
                is_anti_gaspi=is_anti_gaspi_bool,
                limit=limit
            )
        else:
            products = queries.get_home_products(
                product_type=product_type,
                is_anti_gaspi=is_anti_gaspi_bool,
                limit=limit
            )
        
        for product in products:
            product['is_seasonal'] = is_product_in_season(product['name'])
        
        serializer = ProductListSerializer(products, many=True)
        

            
        
        return Response({
            'count': len(serializer.data),
            'filters': {
                'search': search,
                'producer_search': producer_search,
=======
        products = queries.get_home_products(
            product_type=product_type,
            is_anti_gaspi=is_anti_gaspi_bool,
            limit=limit
        )
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'count': len(serializer.data),
            'filters': {
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
                'product_type': product_type,
                'is_anti_gaspi': is_anti_gaspi,
                'limit': limit
            },
            'products': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """
        GET /api/products/{id}/
        Get single product detail.
        """
        product = queries.get_product_detail(pk)
        
        if not product:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
<<<<<<< HEAD
        product['is_seasonal'] = is_product_in_season(product['name'])
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
        
        # Structure producer data
        producer_data = {
            'id': product.pop('producer_id'),
            'shop_name': product.pop('shop_name'),
            'description': product.pop('producer_description'),
            'photo_url': product.pop('producer_photo_url'),
            'city': product.pop('city'),
            'wilaya': product.pop('wilaya'),
            'is_bio_certified': product.pop('is_bio_certified'),
            'user_id': product.pop('user_id'),
            'email': product.pop('email'),
            'phone_number': product.pop('phone_number')
        }
        
        product['producer'] = producer_data
        
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        GET /api/products/search/?q=tomate
        Search products by name or description.
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({
                'error': 'Query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product_type = request.query_params.get('product_type')
        is_anti_gaspi = request.query_params.get('is_anti_gaspi')
        is_anti_gaspi_bool = is_anti_gaspi.lower() == 'true' if is_anti_gaspi else None
        
        products = queries.search_products(
            query=query,
            product_type=product_type,
            is_anti_gaspi=is_anti_gaspi_bool
        )
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'query': query,
            'count': len(serializer.data),
            'filters': {
                'product_type': product_type,
                'is_anti_gaspi': is_anti_gaspi
            },
            'products': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def filter(self, request):
        """
        GET /api/products/filter/?product_type=fresh&min_price=100
        Filter products by multiple criteria.
        """
        sale_type = request.query_params.get('sale_type')
        product_type = request.query_params.get('product_type')
        is_anti_gaspi = request.query_params.get('is_anti_gaspi')
        is_anti_gaspi_bool = is_anti_gaspi.lower() == 'true' if is_anti_gaspi else None
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        wilaya = request.query_params.get('wilaya')
        limit = request.query_params.get('limit')
        
        limit_int = None
        if limit:
            try:
                limit_int = int(limit)
            except:
                pass
        
        products = queries.filter_products(
            sale_type=sale_type,
            product_type=product_type,
            is_anti_gaspi=is_anti_gaspi_bool,
            min_price=min_price,
            max_price=max_price,
            wilaya=wilaya,
            limit=limit_int
        )
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'count': len(serializer.data),
            'filters_applied': {
                'sale_type': sale_type,
                'product_type': product_type,
                'is_anti_gaspi': is_anti_gaspi,
                'min_price': min_price,
                'max_price': max_price,
                'wilaya': wilaya,
                'limit': limit
            },
            'products': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='producer/(?P<producer_id>[^/.]+)')
    def producer_shop(self, request, producer_id=None):
        """
        GET /api/products/producer/{producer_id}/
        Get all products from a specific producer.
        """
        # Get producer info
        producer = queries.get_producer_info(producer_id)
        
        if not producer:
            return Response({
                'error': 'Producer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        product_type = request.query_params.get('product_type')
        is_anti_gaspi = request.query_params.get('is_anti_gaspi')
        is_anti_gaspi_bool = is_anti_gaspi.lower() == 'true' if is_anti_gaspi else None
        
        products = queries.get_producer_products(
            producer_id=producer_id,
            product_type=product_type,
            is_anti_gaspi=is_anti_gaspi_bool
        )
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'shop': {
                'id': producer['id'],
                'shop_name': producer['shop_name'],
                'description': producer.get('description'),
                'photo_url': producer.get('photo_url'),
                'city': producer.get('city'),
                'wilaya': producer.get('wilaya'),
                'is_bio_certified': producer.get('is_bio_certified', False)
            },
            'products_count': len(serializer.data),
            'filters': {
                'product_type': product_type,
                'is_anti_gaspi': is_anti_gaspi
            },
            'products': serializer.data
        })
<<<<<<< HEAD
    @action(detail=False, methods=['get'], url_path='seasonal')
    def seasonal_prodyccts(self, request):



        from datetime import datetime

        limit = int(request.query_params.get('limit', 20))

        all_products = queries.get_home_products(limit=100)


        seasonal = []
        for product  in all_products:
            if is_product_in_season(product['name']):
                product['is_seasonal'] = True
                seasonal.append(product)
        

        seasonal = seasonal[:limit]

        serializer = ProductListSerializer(seasonal,many=True)
        return Response({
            'count':len(serializer.data),
            'season' : datetime.now().strftime('%B'),
            'products' : serializer.data
        })


   
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b


class MyProductViewSet(viewsets.ViewSet):
    """
    ViewSet for authenticated producer product management.
    Requires authentication and IsProducer permission.
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsProducer]
    
    def list(self, request):
        """
        GET /api/my-products/
        Get all products belonging to authenticated producer.
        """
        product_type = request.query_params.get('product_type')
        is_anti_gaspi = request.query_params.get('is_anti_gaspi')
        is_anti_gaspi_bool = is_anti_gaspi.lower() == 'true' if is_anti_gaspi else None
        
        products = queries.get_my_products(
            producer_id=request.user.producer_profile.id,
            product_type=product_type,
            is_anti_gaspi=is_anti_gaspi_bool
        )
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'count': len(serializer.data),
            'filters': {
                'product_type': product_type,
                'is_anti_gaspi': is_anti_gaspi
            },
            'products': serializer.data
        })
    
    def create(self, request):
        """
        POST /api/my-products/
        Create a new product.
        """
        serializer = ProductCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
<<<<<<< HEAD
            # Get photo_url directly - save base64 as-is
            photo_url = serializer.validated_data.get('photo_url')
            
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            product = queries.create_product(
                producer_id=request.user.producer_profile.id,
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description'),
<<<<<<< HEAD
                photo_url=photo_url,  # Save base64 directly
=======
                photo_url=serializer.validated_data.get('photo_url'),
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
                sale_type=serializer.validated_data['sale_type'],
                price=serializer.validated_data['price'],
                stock=serializer.validated_data['stock'],
                product_type=serializer.validated_data['product_type'],
                harvest_date=serializer.validated_data.get('harvest_date'),
                is_anti_gaspi=serializer.validated_data.get('is_anti_gaspi', False)
            )
            
            product_detail = queries.get_my_product_detail(
                product['id'],
                request.user.producer_profile.id
            )
            
            detail_serializer = ProductListSerializer(product_detail)
            
            return Response({
                'message': 'Product created successfully',
                'product': detail_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/my-products/{id}/
        Get single product detail (only if owned by authenticated producer).
        """
        product = queries.get_my_product_detail(
            pk,
            request.user.producer_profile.id
        )
        
        if not product:
            return Response({
                'error': 'Product not found or you do not have permission to access it'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductListSerializer(product)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """
        PUT /api/my-products/{id}/
        Fully update a product.
        """
        product = queries.get_my_product_detail(pk, request.user.producer_profile.id)
        
        if not product:
            return Response({
                'error': 'Product not found or you do not have permission to access it'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
<<<<<<< HEAD
            # Get photo_url directly - save base64 as-is
            photo_url = serializer.validated_data.get('photo_url')
            
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            updated = queries.update_product(
                product_id=pk,
                producer_id=request.user.producer_profile.id,
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description'),
<<<<<<< HEAD
                photo_url=photo_url,  # Save base64 directly
=======
                photo_url=serializer.validated_data.get('photo_url'),
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
                sale_type=serializer.validated_data['sale_type'],
                price=serializer.validated_data['price'],
                stock=serializer.validated_data['stock'],
                product_type=serializer.validated_data['product_type'],
                harvest_date=serializer.validated_data.get('harvest_date'),
                is_anti_gaspi=serializer.validated_data.get('is_anti_gaspi', False)
            )
            
            detail_serializer = ProductListSerializer(updated)
            
            return Response({
                'message': 'Product updated successfully',
                'product': detail_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """
        PATCH /api/my-products/{id}/
        Partially update a product.
        """
        product = queries.get_my_product_detail(pk, request.user.producer_profile.id)
        
        if not product:
            return Response({
                'error': 'Product not found or you do not have permission to access it'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductCreateUpdateSerializer(data=request.data, partial=True)
        
        if serializer.is_valid():
<<<<<<< HEAD
            # Photo URL is already in serializer.validated_data as base64 if provided
            # No conversion needed
            
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            updated = queries.partial_update_product(
                product_id=pk,
                producer_id=request.user.producer_profile.id,
                updates=serializer.validated_data
            )
            
            detail_serializer = ProductListSerializer(updated)
            
            return Response({
                'message': 'Product updated successfully',
                'product': detail_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/my-products/{id}/
        Delete a product.
        """
<<<<<<< HEAD
        # No need to delete image files - base64 is in database
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
        product_name = queries.delete_product(
            pk,
            request.user.producer_profile.id
        )
        
        if product_name:
            return Response({
                'message': f'Product "{product_name}" deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='toggle-anti-gaspi')
    def toggle_anti_gaspi(self, request, pk=None):
        """
        POST /api/my-products/{id}/toggle-anti-gaspi/
        Toggle anti-gaspi status for a product.
        """
        result = queries.toggle_anti_gaspi(
            pk,
            request.user.producer_profile.id
        )
        
        if not result:
            return Response({
                'error': 'Product not found or you do not have permission'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': f'Product {"marked as" if result["is_anti_gaspi"] else "removed from"} anti-gaspi',
            'product': {
                'id': result['id'],
                'name': result['name'],
                'is_anti_gaspi': result['is_anti_gaspi']
            }
<<<<<<< HEAD
        })


# Keep all your basket/subscription viewsets below unchanged...
class SeasonalBasketViewSet(viewsets.ViewSet):
    """
    ViewSet for seasonal basket operations.
    """
    
    # Public endpoints (browsing baskets)
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        GET /api/seasonal-baskets/
        List all active seasonal baskets.
        """
        search = request.query_params.get('search')
        producer_id = request.query_params.get('producer_id')
        limit = int(request.query_params.get('limit', 20))
        
        baskets = queries.get_all_active_baskets(
            search=search,
            producer_id=producer_id,
            limit=limit
        )
        
        serializer = SeasonalBasketSerializer(baskets, many=True)
        
        return Response({
            'count': len(serializer.data),
            'baskets': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """
        GET /api/seasonal-baskets/{id}/
        Get basket details with products.
        """
        basket = queries.get_basket_with_products(pk)
        
        if not basket:
            return Response({
                'error': 'Basket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SeasonalBasketSerializer(basket)
        return Response(serializer.data)

class MySeasonalBasketViewSet(viewsets.ViewSet):
    """
    ViewSet for producer basket management.
    Requires authentication and IsProducer permission.
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsProducer]
    
    def list(self, request):
        """
        GET /api/my-seasonal-baskets/
        Get all baskets for authenticated producer.
        """
        baskets = queries.get_producer_baskets(
            request.user.producer_profile.id
        )
        
        serializer = SeasonalBasketSerializer(baskets, many=True)
        
        return Response({
            'count': len(serializer.data),
            'baskets': serializer.data
        })
    
    def create(self, request):
        """
        POST /api/my-seasonal-baskets/
        Create a new seasonal basket.
        """
        serializer = SeasonalBasketSerializer(data=request.data)
        
        if serializer.is_valid():
            basket = queries.create_seasonal_basket(
                producer_id=request.user.producer_profile.id,
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description'),
                discount_percentage=serializer.validated_data['discount_percentage'],
                original_price=serializer.validated_data['original_price'],
                delivery_frequency=serializer.validated_data.get('delivery_frequency', 'weekly')
            )
            
            result_serializer = SeasonalBasketSerializer(basket)
            
            return Response({
                'message': 'Basket created successfully',
                'basket': result_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/my-seasonal-baskets/{id}/
        Get basket details with products.
        """
        basket = queries.get_basket_with_products(pk)
        
        if not basket or basket['producer_id'] != request.user.producer_profile.id:
            return Response({
                'error': 'Basket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SeasonalBasketSerializer(basket)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """
        PUT/PATCH /api/my-seasonal-baskets/{id}/
        Update basket.
        """
        serializer = SeasonalBasketSerializer(data=request.data, partial=True)
        
        if serializer.is_valid():
            updates = dict(serializer.validated_data)
            
            basket = queries.update_basket(
                pk,
                request.user.producer_profile.id,
                **updates
            )
            
            if not basket:
                return Response({
                    'error': 'Basket not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            result_serializer = SeasonalBasketSerializer(basket)
            
            return Response({
                'message': 'Basket updated successfully',
                'basket': result_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/my-seasonal-baskets/{id}/
        Delete basket.
        """
        basket_name = queries.delete_basket(pk, request.user.producer_profile.id)
        
        if basket_name:
            return Response({
                'message': f'Basket "{basket_name}" deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        
        return Response({
            'error': 'Basket not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='add-product')
    def add_product(self, request, pk=None):
        """
        POST /api/my-seasonal-baskets/{id}/add-product/
        Add product to basket.
        """
        serializer = BasketProductSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verify basket ownership
            basket = queries.get_basket_with_products(pk)
            if not basket or basket['producer_id'] != request.user.producer_profile.id:
                return Response({
                    'error': 'Basket not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            result = queries.add_product_to_basket(
                pk,
                serializer.validated_data['product_id'],
                serializer.validated_data['quantity']
            )
            
            return Response({
                'message': 'Product added to basket',
                'basket_product': result
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='remove-product/(?P<product_id>[^/.]+)')
    def remove_product(self, request, pk=None, product_id=None):
        """
        DELETE /api/my-seasonal-baskets/{id}/remove-product/{product_id}/
        Remove product from basket.
        """
        # Verify basket ownership
        basket = queries.get_basket_with_products(pk)
        if not basket or basket['producer_id'] != request.user.producer_profile.id:
            return Response({
                'error': 'Basket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        success = queries.remove_product_from_basket(pk, product_id)
        
        if success:
            return Response({
                'message': 'Product removed from basket'
            })
        
        return Response({
            'error': 'Product not found in basket'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], url_path='subscribers')
    def subscribers(self, request, pk=None):
        """
        GET /api/my-seasonal-baskets/{id}/subscribers/
        Get list of subscribers.
        """
        subscribers = queries.get_basket_subscribers(
            pk,
            request.user.producer_profile.id
        )
        
        return Response({
            'count': len(subscribers),
            'subscribers': subscribers
        })


class MySubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet for client subscription management.
    Requires authentication.
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        GET /api/my-subscriptions/
        Get all subscriptions for authenticated client.
        """
        # Get client profile
        from users import queries as user_queries
        user_data = user_queries.get_user_by_id(request.user.id)
        
        if user_data['user_type'] != 'client':
            return Response({
                'error': 'Only clients can have subscriptions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        status_filter = request.query_params.get('status')
        
        subscriptions = queries.get_client_subscriptions(
            user_data['client_profile']['id'],
            status=status_filter
        )
        
        serializer = ClientSubscriptionSerializer(subscriptions, many=True)
        
        return Response({
            'count': len(serializer.data),
            'subscriptions': serializer.data
        })
    
    def create(self, request):
        """
        POST /api/my-subscriptions/
        Create a new subscription.
        """
        from users import queries as user_queries
        user_data = user_queries.get_user_by_id(request.user.id)
        
        if user_data['user_type'] != 'client':
            return Response({
                'error': 'Only clients can subscribe'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClientSubscriptionSerializer(data=request.data)
        
        if serializer.is_valid():
            subscription = queries.create_subscription(
                client_id=user_data['client_profile']['id'],
                basket_id=serializer.validated_data['basket_id'],
                delivery_method=serializer.validated_data['delivery_method'],
                delivery_address=serializer.validated_data.get('delivery_address'),
                pickup_point_id=serializer.validated_data.get('pickup_point_id')
            )
            
            result_serializer = ClientSubscriptionSerializer(subscription)
            
            return Response({
                'message': 'Subscription created successfully',
                'subscription': result_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='pause')
    def pause(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/pause/
        Pause subscription.
        """
        from users import queries as user_queries
        user_data = user_queries.get_user_by_id(request.user.id)
        
        result = queries.update_subscription_status(
            pk,
            user_data['client_profile']['id'],
            'paused'
        )
        
        if result:
            return Response({
                'message': 'Subscription paused',
                'subscription': result
            })
        
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/cancel/
        Cancel subscription.
        """
        from users import queries as user_queries
        user_data = user_queries.get_user_by_id(request.user.id)
        
        result = queries.update_subscription_status(
            pk,
            user_data['client_profile']['id'],
            'cancelled'
        )
        
        if result:
            return Response({
                'message': 'Subscription cancelled',
                'subscription': result
            })
        
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='reactivate')
    def reactivate(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/reactivate/
        Reactivate paused subscription.
        """
        from users import queries as user_queries
        user_data = user_queries.get_user_by_id(request.user.id)
        
        result = queries.update_subscription_status(
            pk,
            user_data['client_profile']['id'],
            'active'
        )
        
        if result:
            return Response({
                'message': 'Subscription reactivated',
                'subscription': result
            })
        
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)


class SeasonalBasketViewSet(viewsets.ViewSet):
    """
    ViewSet for seasonal basket operations.
    """
    
    # Public endpoints (browsing baskets)
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        GET /api/seasonal-baskets/
        List all active seasonal baskets.
        """
        search = request.query_params.get('search')
        producer_id = request.query_params.get('producer_id')
        limit = int(request.query_params.get('limit', 20))
        
        baskets = queries.get_all_active_baskets(
            search=search,
            producer_id=producer_id,
            limit=limit
        )
        
        serializer = SeasonalBasketSerializer(baskets, many=True)
        
        return Response({
            'count': len(serializer.data),
            'baskets': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """
        GET /api/seasonal-baskets/{id}/
        Get basket details with products.
        """
        basket = queries.get_basket_with_products(pk)
        
        if not basket:
            return Response({
                'error': 'Basket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SeasonalBasketSerializer(basket)
        return Response(serializer.data)


class MySeasonalBasketViewSet(viewsets.ViewSet):
    """
    ViewSet for producer basket management.
    Requires authentication and IsProducer permission.
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsProducer]
    
    def list(self, request):
        """
        GET /api/my-seasonal-baskets/
        Get all baskets for authenticated producer.
        """
        baskets = queries.get_producer_baskets(
            request.user.producer_profile.id
        )
        
        serializer = SeasonalBasketSerializer(baskets, many=True)
        
        return Response({
            'count': len(serializer.data),
            'baskets': serializer.data
        })
    
    def create(self, request):
        """
        POST /api/my-seasonal-baskets/
        Create a new seasonal basket.
        """
        serializer = SeasonalBasketSerializer(data=request.data)
        
        if serializer.is_valid():
            basket = queries.create_seasonal_basket(
                producer_id=request.user.producer_profile.id,
                name=serializer.validated_data['name'],
                description=serializer.validated_data.get('description'),
                discount_percentage=serializer.validated_data['discount_percentage'],
                original_price=serializer.validated_data['original_price'],
                delivery_frequency=serializer.validated_data.get('delivery_frequency', 'weekly')
            )
            
            result_serializer = SeasonalBasketSerializer(basket)
            
            return Response({
                'message': 'Basket created successfully',
                'basket': result_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/my-seasonal-baskets/{id}/
        Get basket details with products.
        """
        basket = queries.get_basket_with_products(pk)
        
        if not basket or basket['producer_id'] != request.user.producer_profile.id:
            return Response({
                'error': 'Basket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SeasonalBasketSerializer(basket)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """
        PUT/PATCH /api/my-seasonal-baskets/{id}/
        Update basket.
        """
        serializer = SeasonalBasketSerializer(data=request.data, partial=True)
        
        if serializer.is_valid():
            updates = dict(serializer.validated_data)
            
            basket = queries.update_basket(
                pk,
                request.user.producer_profile.id,
                **updates
            )
            
            if not basket:
                return Response({
                    'error': 'Basket not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            result_serializer = SeasonalBasketSerializer(basket)
            
            return Response({
                'message': 'Basket updated successfully',
                'basket': result_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        DELETE /api/my-seasonal-baskets/{id}/
        Delete basket.
        """
        basket_name = queries.delete_basket(pk, request.user.producer_profile.id)
        
        if basket_name:
            return Response({
                'message': f'Basket "{basket_name}" deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        
        return Response({
            'error': 'Basket not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='add-product')
    def add_product(self, request, pk=None):
        """
        POST /api/my-seasonal-baskets/{id}/add-product/
        Add product to basket.
        """
        serializer = BasketProductSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verify basket ownership
            basket = queries.get_basket_with_products(pk)
            if not basket or basket['producer_id'] != request.user.producer_profile.id:
                return Response({
                    'error': 'Basket not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            result = queries.add_product_to_basket(
                pk,
                serializer.validated_data['product_id'],
                serializer.validated_data['quantity']
            )
            
            return Response({
                'message': 'Product added to basket',
                'basket_product': result
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='remove-product/(?P<product_id>[^/.]+)')
    def remove_product(self, request, pk=None, product_id=None):
        """
        DELETE /api/my-seasonal-baskets/{id}/remove-product/{product_id}/
        Remove product from basket.
        """
        # Verify basket ownership
        basket = queries.get_basket_with_products(pk)
        if not basket or basket['producer_id'] != request.user.producer_profile.id:
            return Response({
                'error': 'Basket not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        success = queries.remove_product_from_basket(pk, product_id)
        
        if success:
            return Response({
                'message': 'Product removed from basket'
            })
        
        return Response({
            'error': 'Product not found in basket'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], url_path='subscribers')
    def subscribers(self, request, pk=None):
        """
        GET /api/my-seasonal-baskets/{id}/subscribers/
        Get list of subscribers.
        """
        subscribers = queries.get_basket_subscribers(
            pk,
            request.user.producer_profile.id
        )
        
        return Response({
            'count': len(subscribers),
            'subscribers': subscribers
        })


class MySubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet for client subscription management.
    Requires authentication.
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        GET /api/my-subscriptions/
        Get all subscriptions for authenticated client.
        """
        # Get client profile
        from users import queries as user_queries
        user_row = user_queries.get_user_by_id(request.user.id)
        user_data = user_queries.structure_user_data(user_row)  # ✅ ADDED
        
        if user_data['user_type'] != 'client':
            return Response({
                'error': 'Only clients can have subscriptions'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if client_profile exists
        client_profile = user_data.get('client_profile')
        if not client_profile or not client_profile.get('id'):
            return Response({
                'error': 'Client profile not found. Please complete your profile.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        status_filter = request.query_params.get('status')
        
        subscriptions = queries.get_client_subscriptions(
            client_profile['id'],
            status=status_filter
        )
        
        serializer = ClientSubscriptionSerializer(subscriptions, many=True)
        
        return Response({
            'count': len(serializer.data),
            'subscriptions': serializer.data
        })
    
    def create(self, request):
        """
        POST /api/my-subscriptions/
        Create a new subscription.
        """
        from users import queries as user_queries
        user_row = user_queries.get_user_by_id(request.user.id)
        user_data = user_queries.structure_user_data(user_row)  # ✅ ADDED
        
        if user_data['user_type'] != 'client':
            return Response({
                'error': 'Only clients can subscribe'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if client_profile exists
        client_profile = user_data.get('client_profile')
        if not client_profile or not client_profile.get('id'):
            return Response({
                'error': 'Client profile not found. Please complete your profile.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ClientSubscriptionSerializer(data=request.data)
        
        if serializer.is_valid():
            subscription = queries.create_subscription(
                client_id=client_profile['id'],
                basket_id=serializer.validated_data['basket_id'],
                delivery_method=serializer.validated_data['delivery_method'],
                delivery_address=serializer.validated_data.get('delivery_address'),
                pickup_point_id=serializer.validated_data.get('pickup_point_id')
            )
            
            result_serializer = ClientSubscriptionSerializer(subscription)
            
            return Response({
                'message': 'Subscription created successfully',
                'subscription': result_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='pause')
    def pause(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/pause/
        Pause subscription.
        """
        from users import queries as user_queries
        user_row = user_queries.get_user_by_id(request.user.id)
        user_data = user_queries.structure_user_data(user_row)  # ✅ ADDED
        
        # Check if client_profile exists
        client_profile = user_data.get('client_profile')
        if not client_profile or not client_profile.get('id'):
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = queries.update_subscription_status(
            pk,
            client_profile['id'],
            'paused'
        )
        
        if result:
            return Response({
                'message': 'Subscription paused',
                'subscription': result
            })
        
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/cancel/
        Cancel subscription.
        """
        from users import queries as user_queries
        user_row = user_queries.get_user_by_id(request.user.id)
        user_data = user_queries.structure_user_data(user_row)  # ✅ ADDED
        
        # Check if client_profile exists
        client_profile = user_data.get('client_profile')
        if not client_profile or not client_profile.get('id'):
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = queries.update_subscription_status(
            pk,
            client_profile['id'],
            'cancelled'
        )
        
        if result:
            return Response({
                'message': 'Subscription cancelled',
                'subscription': result
            })
        
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='reactivate')
    def reactivate(self, request, pk=None):
        """
        POST /api/my-subscriptions/{id}/reactivate/
        Reactivate paused subscription.
        """
        from users import queries as user_queries
        user_row = user_queries.get_user_by_id(request.user.id)
        user_data = user_queries.structure_user_data(user_row)  # ✅ ADDED
        
        # Check if client_profile exists
        client_profile = user_data.get('client_profile')
        if not client_profile or not client_profile.get('id'):
            return Response({
                'error': 'Client profile not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = queries.update_subscription_status(
            pk,
            client_profile['id'],
            'active'
        )
        
        if result:
            return Response({
                'message': 'Subscription reactivated',
                'subscription': result
            })
        
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
=======
        })
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
