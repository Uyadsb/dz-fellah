from rest_framework import permissions

class IsProducer(permissions.BasePermission):
    """Only producers can access."""
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, 'user'):
            return False
        return hasattr(request.user, 'user_type') and request.user.user_type == 'producer'



class CanBuyProducts(permissions.BasePermission):
    """Both producers and clients can buy."""
    
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, 'user'):
            return False
        return hasattr(request.user, 'user_type') and request.user.user_type in ['producer', 'client']


class IsProducerOrReadOnly(permissions.BasePermission):
    """Anyone can view, only producers can create."""
    
    def has_permission(self, request, view):
        # Allow read operations for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations only for producers
        if not request.user or not hasattr(request, 'user'):
            return False
        
        return hasattr(request.user, 'user_type') and request.user.user_type == 'producer'


class IsProductOwner(permissions.BasePermission):
    """Only product owner can edit/delete."""
    
    def has_object_permission(self, request, view, obj):
        # Allow read operations for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, check ownership
        # obj here is expected to be a product dictionary with 'producer_id'
        if hasattr(obj, 'get'):
            # If obj is a dictionary
            producer_id = obj.get('producer_id')
            if producer_id and hasattr(request.user, 'producer_profile'):
                return request.user.producer_profile.id == producer_id
        
        # If obj has producer attribute (model-like)
        if hasattr(obj, 'producer'):
            if hasattr(request.user, 'producer_profile'):
                return obj.producer.id == request.user.producer_profile.id
        
        return False