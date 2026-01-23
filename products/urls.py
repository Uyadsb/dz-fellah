from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
        ProductViewSet, 
        MyProductViewSet,
        SeasonalBasketViewSet,
        MySeasonalBasketViewSet,
        MySubscriptionViewSet
    )
from . import views_ratings
from .cron_views import trigger_anti_gaspi_cron

    
router = DefaultRouter()

    
router.register(r'products', ProductViewSet, basename='product')
router.register(r'my-products', MyProductViewSet, basename='my-product')
router.register(r'seasonal-baskets', SeasonalBasketViewSet, basename='seasonal-basket')
router.register(r'my-seasonal-baskets', MySeasonalBasketViewSet, basename='my-seasonal-basket')
router.register(r'my-subscriptions', MySubscriptionViewSet, basename='my-subscription')

urlpatterns = [
        
        path('products/rate/', views_ratings.create_product_rating, name='create_product_rating'),
        path('products/<int:product_id>/ratings/', views_ratings.get_product_ratings, name='get_product_ratings'),
        path('products/<int:product_id>/my-rating/', views_ratings.get_my_product_rating, name='get_my_product_rating'),
        path('products/<int:product_id>/rating/', views_ratings.delete_product_rating_view, name='delete_product_rating'),
        path('products/producer/<int:producer_id>/rating/', views_ratings.get_producer_rating_view, name='get_producer_rating'),
        path('products/<int:product_id>/debug-purchase/', views_ratings.debug_purchase_check, name='debug_purchase'),
        path('cron/anti-gaspi/', trigger_anti_gaspi_cron, name='cron_anti_gaspi'),
        
        
        
        path('', include(router.urls)),
    ]
