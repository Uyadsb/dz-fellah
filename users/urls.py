from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, ProducerViewSet

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'producers', ProducerViewSet, basename='producer')

urlpatterns = [
    path('', include(router.urls)),
]