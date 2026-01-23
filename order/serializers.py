from rest_framework import serializers
from .models import Order, SubOrder, OrderItem
from decimal import Decimal


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items de commande."""
    
    subtotal = serializers.SerializerMethodField()
    price_adjustment = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_id',
            'product_name',
            'quantity_ordered',
            'quantity_actual',
            'unit_price',
            'sale_type',
            'subtotal',
            'price_adjustment',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_subtotal(self, obj):
        """Sous-total de cet item."""
        return float(obj.get_subtotal())
    
    def get_price_adjustment(self, obj):
        """Ajustement de prix si quantité réelle différente."""
        return float(obj.get_price_adjustment())


class SubOrderSerializer(serializers.ModelSerializer):
    """Serializer pour les sous-commandes."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    producer_details = serializers.SerializerMethodField()
    client_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SubOrder
        fields = [
            'id',
            'sub_order_number',
            'producer_id',
            'producer_details',
            'client_details',
            'status',
            'subtotal',
            'total',
            'items',
            'producer_notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'sub_order_number',
            'producer_id',
            'created_at',
            'updated_at'
        ]
    
    def get_total(self, obj):
        """Total de cette sous-commande."""
        return float(obj.get_total())
    
    def get_producer_details(self, obj):
        """Détails du producteur."""
        from db import users_queries
        producer = users_queries.get_producer_profile_by_id(obj.producer_id)
        
        if not producer:
            return None
        
        return {
            'id': producer['id'],
            'shop_name': producer['shop_name'],
            'city': producer.get('city'),
            'wilaya': producer.get('wilaya'),
            'phone': producer.get('phone'),
            'address': producer.get('address'),
        }
    
    def get_client_details(self, obj):
        """Détails du client depuis la commande parent."""
        try:
            from db import users_queries
            
            # Get user data from parent order's client_id
            user = users_queries.get_user_by_id(obj.parent_order.client_id)
            
            if not user:
                return {
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'phone': '',
                    'avatar': None
                }
            
            # Get client profile for avatar
            client_profile = user.get('client_profile', {})
            
            return {
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'email': user.get('email', ''),
                'phone': user.get('phone', ''),
                'avatar': client_profile.get('avatar') if client_profile else None
            }
        except Exception as e:
            print(f"Error getting client details: {e}")
            return {
                'first_name': '',
                'last_name': '',
                'email': '',
                'phone': '',
                'avatar': None
            }


class OrderSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes complètes."""
    
    sub_orders = SubOrderSerializer(many=True, read_only=True)
    sub_orders_count = serializers.SerializerMethodField()
    client_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'client_id',
            'client_details',
            'status',
            'total_amount',
            'delivery_method',
            'delivery_address',
            'notes',
            'sub_orders',
            'sub_orders_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'order_number',
            'client_id',
            'total_amount',
            'created_at',
            'updated_at'
        ]
    
    def get_sub_orders_count(self, obj):
        """Nombre de sous-commandes."""
        return obj.get_sub_orders_count()
    
    def get_client_details(self, obj):
        """Détails du client."""
        from db import users_queries
        user = users_queries.get_user_by_id(obj.client_id)
        
        if not user:
            return None
        
        return {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'phone': user.get('phone'),
        }


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des commandes."""
    
    sub_orders_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'total_amount',
            'delivery_method',
            'sub_orders_count',
            'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at']
    
    def get_sub_orders_count(self, obj):
        """Nombre de producteurs dans cette commande."""
        return obj.get_sub_orders_count()


class CreateOrderSerializer(serializers.Serializer):
    """Serializer pour créer une commande depuis le panier."""
    
    delivery_method = serializers.ChoiceField(
        choices=['pickup_producer', 'pickup_point'],
        default='pickup_producer'
    )
    
    delivery_address = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )
    
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )
    
    def validate(self, data):
        """Validation des données de commande."""
        if data['delivery_method'] == 'pickup_point' and not data.get('delivery_address'):
            raise serializers.ValidationError({
                'delivery_address': 'Adresse requise pour le retrait en point de collecte'
            })
        
        return data


class UpdateSubOrderStatusSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'une sous-commande (producteur)."""
    
    status = serializers.ChoiceField(
        choices=['confirmed', 'preparing', 'ready', 'completed', 'cancelled']
    )
    
    producer_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )


class AdjustOrderItemQuantitySerializer(serializers.Serializer):
    """
    Serializer pour ajuster la quantité réelle d'un item (pour produits au poids).
    Utilisé par le producteur lors de la préparation.
    """
    
    quantity_actual = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01
    )
    
    def validate_quantity_actual(self, value):
        """Vérifie que la quantité réelle est raisonnable."""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        
        # Vérifier que l'ajustement n'est pas trop important (±30%)
        item = self.context.get('item')
        if item:
            min_qty = item.quantity_ordered * Decimal('0.7')
            max_qty = item.quantity_ordered * Decimal('1.3')
            
            if value < min_qty or value > max_qty:
                raise serializers.ValidationError(
                    f"L'ajustement doit être entre {min_qty} et {max_qty} "
                    f"(±30% de {item.quantity_ordered})"
                )
        
        return value