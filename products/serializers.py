from rest_framework import serializers
from decimal import Decimal


class ProductListSerializer(serializers.Serializer):
    """Lightweight serializer for product lists."""
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    photo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    sale_type = serializers.ChoiceField(choices=['unit', 'weight'])
    stock = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_type = serializers.ChoiceField(choices=[
    'Vegetables', 'Fruits', 'Dairy', 'Oils', 
    'Honey', 'Grains', 'Meat', 'Other'
])
    is_anti_gaspi = serializers.BooleanField()
    harvest_date = serializers.DateField(allow_null=True, required=False)
    producer_id = serializers.IntegerField(read_only=True)
    producer_name = serializers.CharField(read_only=True)
    is_seasonal = serializers.BooleanField(required=False)


class ProducerInfoSerializer(serializers.Serializer):
    """Producer info for product detail."""
    
    id = serializers.IntegerField(read_only=True)
    shop_name = serializers.CharField()
    description = serializers.CharField(allow_null=True, required=False)
    photo_url = serializers.CharField(allow_null=True, required=False)
    city = serializers.CharField(allow_null=True, required=False)
    wilaya = serializers.CharField(allow_null=True, required=False)
    is_bio_certified = serializers.BooleanField()
    user_id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(read_only=True)


class ProductDetailSerializer(serializers.Serializer):
    """Detailed serializer with full producer info."""
    
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_null=True, required=False)
    photo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sale_type = serializers.ChoiceField(choices=['unit', 'weight'])
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_type = serializers.ChoiceField(choices=[
    'Vegetables', 'Fruits', 'Dairy', 'Oils', 
    'Honey', 'Grains', 'Meat', 'Other'
])
    harvest_date = serializers.DateField(allow_null=True, required=False)
    is_anti_gaspi = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_seasonal = serializers.BooleanField(required=False)
    
    
    producer = ProducerInfoSerializer(read_only=True)


class ProductCreateUpdateSerializer(serializers.Serializer):
    """Serializer for creating/updating products."""
    
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    photo_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sale_type = serializers.ChoiceField(choices=['unit', 'weight'])
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_type = serializers.ChoiceField(choices=[
    'Vegetables', 'Fruits', 'Dairy', 'Oils', 
    'Honey', 'Grains', 'Meat', 'Other'
])
    harvest_date = serializers.DateField(allow_null=True, required=False)
    is_anti_gaspi = serializers.BooleanField(required=False, default=False)
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
    
    def validate(self, data):
    # Optional: Add validation for fresh products (Vegetables, Fruits, Dairy)
     fresh_categories = ['Vegetables', 'Fruits', 'Dairy']
     if data.get('product_type') in fresh_categories and not data.get('harvest_date'):
         # Optional: You could add a warning here if needed
        pass
     return data


class SeasonalBasketSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    producer_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    delivery_frequency = serializers.ChoiceField(
        choices=['weekly', 'biweekly', 'monthly'],
        default='weekly'
    )
    is_active = serializers.BooleanField(default=True)
    subscriber_count = serializers.IntegerField(read_only=True, required=False)
    product_count = serializers.IntegerField(read_only=True, required=False)
    producer_shop_name = serializers.CharField(read_only=True, required=False)
    producer_banner = serializers.CharField(read_only=True, required=False) 
    products = serializers.ListField(read_only=True, required=False)
    pickup_day = serializers.CharField(max_length=20, required=False)

class BasketProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)


class ClientSubscriptionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    basket_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=['active', 'paused', 'cancelled'],
        default='active',
        read_only=True
    )
    delivery_method = serializers.ChoiceField(
        choices=['pickup_producer', 'pickup_point']
    )
    delivery_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pickup_point_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    start_date = serializers.DateField(read_only=True)
    next_delivery_date = serializers.DateField(read_only=True)
    total_deliveries = serializers.IntegerField(read_only=True)
    
    # ✅ ADD ALL BASKET FIELDS FROM QUERY
    basket_name = serializers.CharField(read_only=True, required=False)
    basket_description = serializers.CharField(read_only=True, required=False, allow_blank=True, allow_null=True)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, required=False)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, required=False)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, required=False)
    delivery_frequency = serializers.CharField(read_only=True, required=False)
    pickup_day = serializers.CharField(read_only=True, required=False)
    
    # ✅ ADD PRODUCER FIELDS
    producer_id = serializers.IntegerField(read_only=True, required=False)
    shop_name = serializers.CharField(read_only=True, required=False)
    city = serializers.CharField(read_only=True, required=False)
    wilaya = serializers.CharField(read_only=True, required=False)
    producer_banner = serializers.CharField(read_only=True, required=False, allow_blank=True, allow_null=True)
    product_count = serializers.IntegerField(read_only=True, required=False)