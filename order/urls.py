from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ProducerOrderViewSet

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'producer-orders', ProducerOrderViewSet, basename='producer-order')

urlpatterns = [
    path('', include(router.urls)),
]