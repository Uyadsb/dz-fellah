from rest_framework import serializers


class ProducerProfileSerializer(serializers.Serializer):
    """Serializer for ProducerProfile."""
    
    id = serializers.IntegerField(read_only=True)
    shop_name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    photo_url = serializers.CharField(max_length=500, allow_null=True, required=False, allow_blank=True)
<<<<<<< HEAD
    avatar = serializers.CharField(max_length=500, allow_null=True, required=False, allow_blank=True)  # NEW
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    address = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    wilaya = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    methods = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    is_bio_certified = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)


class ClientProfileSerializer(serializers.Serializer):
    """Serializer for ClientProfile."""
    
    id = serializers.IntegerField(read_only=True)
<<<<<<< HEAD
    avatar = serializers.CharField(max_length=500, allow_null=True, required=False, allow_blank=True)  # NEW
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    address = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    wilaya = serializers.CharField(max_length=100, allow_null=True, required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)


class UserSerializer(serializers.Serializer):
    """Serializer for User model (read operations)."""
    
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField()
    user_type = serializers.ChoiceField(choices=['producer', 'client'])
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, allow_null=True, required=False)
    is_active = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    
    producer_profile = ProducerProfileSerializer(read_only=True, allow_null=True)
    client_profile = ClientProfileSerializer(read_only=True, allow_null=True)


class RegisterProducerSerializer(serializers.Serializer):
    """Serializer for producer registration."""
    
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Producer profile fields
    shop_name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
<<<<<<< HEAD
    avatar = serializers.CharField(max_length=500, required=False, allow_blank=True)  # NEW
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    wilaya = serializers.CharField(max_length=100, required=False, allow_blank=True)
    methods = serializers.CharField(required=False, allow_blank=True)
    is_bio_certified = serializers.BooleanField(required=False, default=False)
    
    def validate_password(self, value):
        """Validate password strength."""
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        return value


class RegisterClientSerializer(serializers.Serializer):
    """Serializer for client registration."""
    
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Client profile fields
<<<<<<< HEAD
    avatar = serializers.CharField(max_length=500, required=False, allow_blank=True)  # NEW
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    wilaya = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_password(self, value):
        """Validate password strength."""
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)