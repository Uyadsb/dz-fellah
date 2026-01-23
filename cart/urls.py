from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]