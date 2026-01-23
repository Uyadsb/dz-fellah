from rest_framework_simplejwt.authentication import JWTAuthentication
from . import queries


class CustomUser:
    """
    Custom user object to work with DRF permissions.
    Mimics Django's User model interface.
    """
    
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.user_type = user_data['user_type']
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        self.phone = user_data.get('phone')
        self.is_active = user_data['is_active']
        self.is_verified = user_data['is_verified']
        
        # Store producer_profile data
        if user_data.get('producer_profile'):
            self.producer_profile = type('obj', (object,), {
                'id': user_data['producer_profile']['id'],
                'shop_name': user_data['producer_profile']['shop_name'],
                'city': user_data['producer_profile'].get('city'),
                'wilaya': user_data['producer_profile'].get('wilaya'),
            })()
        else:
            self.producer_profile = None
        
        # Store client_profile data
        if user_data.get('client_profile'):
            self.client_profile = type('obj', (object,), {
                'id': user_data['client_profile']['id'],
                'city': user_data['client_profile'].get('city'),
                'wilaya': user_data['client_profile'].get('wilaya'),
            })()
        else:
            self.client_profile = None
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users."""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for authenticated users."""
        return False
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication to use raw SQL queries."""
    
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
            
            # Get user data from raw SQL
            user_data = queries.get_user_by_id(user_id)
            
            if not user_data or not user_data['is_active']:
                return None
            
            # Structure user data
            user_structured = queries.structure_user_data(user_data)
            
            # Return CustomUser object
            return CustomUser(user_structured)
            
        except Exception:
            return None