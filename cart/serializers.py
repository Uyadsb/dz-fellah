from rest_framework import serializers
from .models import Cart, CartItem
from decimal import Decimal


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items du panier."""
    
    subtotal = serializers.SerializerMethodField()
    product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'quantity',
            'price_snapshot',
            'subtotal',
            'product_details',
            'added_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at', 'price_snapshot']
    
    def get_subtotal(self, obj):
        """Calcule le sous-total pour cet item."""
        return float(obj.get_subtotal())
    
    def get_product_details(self, obj):
        """
        Récupère les détails du produit depuis les queries SQL.
        """
        from products import queries as product_queries
        product = product_queries.get_product_detail(obj.product_id)
        
        if not product:
            return None
        
        return {
            'id': product['id'],
            'name': product['name'],
            'photo_url': product.get('photo_url'),
            'sale_type': product['sale_type'],
            'product_type': product['product_type'],
            'current_price': float(product['price']),
            'stock': float(product['stock']),
            'is_anti_gaspi': product.get('is_anti_gaspi', False),
            'producer': {
                'id': product['producer_id'],
                'shop_name': product['shop_name'],
                'city': product.get('city'),
                'wilaya': product.get('wilaya'),
            }
        }


class CartSerializer(serializers.ModelSerializer):
    """Serializer pour le panier complet."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    items_by_producer = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'user_id',
            'items',
            'items_count',
            'total',
            'items_by_producer',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        """Calcule le total du panier."""
        return float(obj.get_total())
    
    def get_items_count(self, obj):
        """Nombre d'items dans le panier."""
        return obj.get_items_count()
    
    def get_items_by_producer(self, obj):
        """
        Groupe les items par producteur.
        Utile pour afficher le panier organisé par producteur.
        """
        items_by_producer = {}
        
        for item in obj.items.all():
            product = item.get_product_details()
            if not product:
                continue
            
            producer_id = str(product['producer_id'])
            
            if producer_id not in items_by_producer:
                items_by_producer[producer_id] = {
                    'producer_id': product['producer_id'],
                    'shop_name': product['shop_name'],
                    'city': product.get('city'),
                    'wilaya': product.get('wilaya'),
                    'items': [],
                    'subtotal': 0.0
                }
            
            item_data = CartItemSerializer(item).data
            items_by_producer[producer_id]['items'].append(item_data)
            items_by_producer[producer_id]['subtotal'] += float(item.get_subtotal())
        
        return list(items_by_producer.values())


class AddToCartSerializer(serializers.Serializer):
    """Serializer pour ajouter un produit au panier."""
    
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    
    def validate_product_id(self, value):
        """Vérifie que le produit existe."""
        from products import queries as product_queries
        product = product_queries.get_product_detail(value)
        
        if not product:
            raise serializers.ValidationError("Produit introuvable")
        
        return value
    
    def validate(self, data):
        """Valide la quantité par rapport au stock disponible."""
        from products import queries as product_queries
        
        product = product_queries.get_product_detail(data['product_id'])
        
        if data['quantity'] > product['stock']:
            raise serializers.ValidationError({
                'quantity': f"Stock insuffisant. Disponible : {product['stock']}"
            })
        
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer pour mettre à jour la quantité d'un item."""
    
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    
    def validate_quantity(self, value):
        """Vérifie que la quantité est valide."""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        return value