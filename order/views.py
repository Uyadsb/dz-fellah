from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from decimal import Decimal

from .models import Order, SubOrder, OrderItem
from cart.models import Cart
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    SubOrderSerializer,
    CreateOrderSerializer,
    UpdateSubOrderStatusSerializer,
    AdjustOrderItemQuantitySerializer
)
from users.authentication import CustomJWTAuthentication
from users.permissions import IsProducer, CanBuyProducts


class OrderViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les commandes (côté client).
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, CanBuyProducts]
    
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """
        POST /api/orders/create_from_cart/
        Crée une commande à partir du panier.
        
        Body:
        {
            "delivery_method": "pickup_producer",
            "delivery_address": "Optionnel",
            "notes": "Instructions spéciales"
        }
        """
        serializer = CreateOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Récupérer le panier
            cart = Cart.objects.get(user_id=request.user.id)
            
            if not cart.items.exists():
                return Response({
                    'error': 'Votre panier est vide'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # 1. Créer la commande parent
                order = Order.objects.create(
                    client_id=request.user.id,
                    status='pending',
                    delivery_method=serializer.validated_data['delivery_method'],
                    delivery_address=serializer.validated_data.get('delivery_address', ''),
                    notes=serializer.validated_data.get('notes', '')
                )
                
                # 2. Grouper les items par producteur
                items_by_producer = {}
                from products import queries as product_queries
                
                for cart_item in cart.items.all():
                    product = product_queries.get_product_detail(cart_item.product_id)
                    
                    if not product:
                        raise ValueError(f"Produit {cart_item.product_id} introuvable")
                    
                    # Vérifier le stock
                    if cart_item.quantity > product['stock']:
                        raise ValueError(
                            f"Stock insuffisant pour {product['name']}. "
                            f"Disponible : {product['stock']}"
                        )
                    
                    producer_id = product['producer_id']
                    
                    if producer_id not in items_by_producer:
                        items_by_producer[producer_id] = []
                    
                    items_by_producer[producer_id].append({
                        'cart_item': cart_item,
                        'product': product
                    })
                
                # 3. Créer une sous-commande par producteur
                for producer_id, items in items_by_producer.items():
                    # Créer la sous-commande
                    sub_order = SubOrder.objects.create(
                        parent_order=order,
                        producer_id=producer_id,
                        status='pending'
                    )
                    
                    # Créer les items de commande
                    subtotal = Decimal('0.00')
                    
                    for item_data in items:
                        cart_item = item_data['cart_item']
                        product = item_data['product']
                        
                        order_item = OrderItem.objects.create(
                            sub_order=sub_order,
                            product_id=product['id'],
                            product_name=product['name'],
                            quantity_ordered=cart_item.quantity,
                            unit_price=cart_item.price_snapshot,
                            sale_type=product['sale_type']
                        )
                        
                        subtotal += order_item.get_subtotal()
                        
                        # Décrémenter le stock
                        # Note: Dans un système réel, il faudrait utiliser une transaction SQL
                        # ou un mécanisme de verrouillage pour éviter les race conditions
                        new_stock = product['stock'] - cart_item.quantity
                        product_queries.partial_update_product(
                            product_id=product['id'],
                            producer_id=producer_id,
                            updates={'stock': new_stock}
                        )
                    
                    # Mettre à jour le subtotal de la sous-commande
                    sub_order.subtotal = subtotal
                    sub_order.save()
                
                # 4. Mettre à jour le total de la commande
                order.update_total()
                
                # 5. Vider le panier
                cart.items.all().delete()
                
                # 6. Retourner la commande créée
                order_serializer = OrderSerializer(order)
                
                return Response({
                    'message': 'Commande créée avec succès',
                    'order': order_serializer.data
                }, status=status.HTTP_201_CREATED)
        
        except Cart.DoesNotExist:
            return Response({
                'error': 'Panier introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la création de la commande : {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        GET /api/orders/my_orders/
        Liste toutes les commandes du client.
        """
        orders = Order.objects.filter(client_id=request.user.id).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        
        return Response({
            'count': orders.count(),
            'orders': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """
        GET /api/orders/{id}/
        Détails d'une commande spécifique.
        """
        try:
            order = Order.objects.get(id=pk, client_id=request.user.id)
            serializer = OrderSerializer(order)
            
            return Response({
                'order': serializer.data
            })
        
        except Order.DoesNotExist:
            return Response({
                'error': 'Commande introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/orders/{id}/cancel/
        Annule une commande (seulement si status = pending ou confirmed).
        """
        try:
            order = Order.objects.get(id=pk, client_id=request.user.id)
            
            if order.status not in ['pending', 'confirmed']:
                return Response({
                    'error': 'Cette commande ne peut plus être annulée'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Annuler toutes les sous-commandes
                for sub_order in order.sub_orders.all():
                    sub_order.status = 'cancelled'
                    sub_order.save()
                    
                    # Remettre les produits en stock
                    from products import queries as product_queries
                    
                    for item in sub_order.items.all():
                        product = product_queries.get_product_detail(item.product_id)
                        if product:
                            new_stock = product['stock'] + item.quantity_ordered
                            product_queries.partial_update_product(
                                product_id=item.product_id,
                                producer_id=sub_order.producer_id,
                                updates={'stock': new_stock}
                            )
                
                # Mettre à jour le statut de la commande
                order.status = 'cancelled'
                order.save()
            
            return Response({
                'message': 'Commande annulée avec succès',
                'order': OrderSerializer(order).data
            })
        
        except Order.DoesNotExist:
            return Response({
                'error': 'Commande introuvable'
            }, status=status.HTTP_404_NOT_FOUND)


<<<<<<< HEAD


=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
class ProducerOrderViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les commandes (côté producteur).
    Les producteurs ne voient que leurs sous-commandes.
<<<<<<< HEAD
    
    
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, IsProducer]
    
<<<<<<< HEAD
    def get_producer_id(self, request):
        """
         Safely get producer ID with proper error handling.
        Returns None if user doesn't have a producer profile.
        """
        # Check if the attribute exists
        if not hasattr(request.user, 'producer_profile'):
            return None
        
        # Check if it's not None
        producer_profile = request.user.producer_profile
        if not producer_profile:
            return None
        
        # Safe to access ID now
        return producer_profile.id
    
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """
        GET /api/producer-orders/my_orders/
        Liste toutes les sous-commandes du producteur.
        """
<<<<<<< HEAD
        # ✅ FIXED: Check producer_id safely
        producer_id = self.get_producer_id(request)
        
        if not producer_id:
            return Response({
                'error': 'Profil producteur requis'
            }, status=status.HTTP_403_FORBIDDEN)
        
        sub_orders = SubOrder.objects.filter(
            producer_id=producer_id
=======
        sub_orders = SubOrder.objects.filter(
            producer_id=request.user.producer_profile.id
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
        ).select_related('parent_order').order_by('-created_at')
        
        serializer = SubOrderSerializer(sub_orders, many=True)
        
        return Response({
            'count': sub_orders.count(),
            'sub_orders': serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """
        GET /api/producer-orders/{id}/
        Détails d'une sous-commande spécifique.
        """
<<<<<<< HEAD
        # ✅ FIXED: Check producer_id safely
        producer_id = self.get_producer_id(request)
        
        if not producer_id:
            return Response({
                'error': 'Profil producteur requis'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            sub_order = SubOrder.objects.get(
                id=pk,
                producer_id=producer_id
=======
        try:
            sub_order = SubOrder.objects.get(
                id=pk,
                producer_id=request.user.producer_profile.id
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            )
            serializer = SubOrderSerializer(sub_order)
            
            return Response({
                'sub_order': serializer.data
            })
        
        except SubOrder.DoesNotExist:
            return Response({
                'error': 'Commande introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        PATCH /api/producer-orders/{id}/update_status/
        Met à jour le statut d'une sous-commande.
        
        Body:
        {
            "status": "confirmed",
            "producer_notes": "Commande prête demain"
        }
        """
<<<<<<< HEAD
        # ✅ FIXED: Check producer_id safely
        producer_id = self.get_producer_id(request)
        
        if not producer_id:
            return Response({
                'error': 'Profil producteur requis'
            }, status=status.HTTP_403_FORBIDDEN)
        
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
        serializer = UpdateSubOrderStatusSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sub_order = SubOrder.objects.get(
                id=pk,
<<<<<<< HEAD
                producer_id=producer_id
=======
                producer_id=request.user.producer_profile.id
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            )
            
            # Mettre à jour le statut
            sub_order.status = serializer.validated_data['status']
            
            if 'producer_notes' in serializer.validated_data:
                sub_order.producer_notes = serializer.validated_data['producer_notes']
            
            sub_order.save()
            
            # Mettre à jour le statut global de la commande parent
            sub_order.parent_order.update_global_status()
            
            return Response({
                'message': 'Statut mis à jour',
                'sub_order': SubOrderSerializer(sub_order).data
            })
        
        except SubOrder.DoesNotExist:
            return Response({
                'error': 'Commande introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['patch'], url_path='adjust_item/(?P<item_id>[^/.]+)')
    def adjust_item_quantity(self, request, pk=None, item_id=None):
        """
        PATCH /api/producer-orders/{id}/adjust_item/{item_id}/
        Ajuste la quantité réelle d'un item (pour produits au poids).
        
        Body:
        {
            "quantity_actual": 2.3
        }
        """
<<<<<<< HEAD
        # ✅ FIXED: Check producer_id safely
        producer_id = self.get_producer_id(request)
        
        if not producer_id:
            return Response({
                'error': 'Profil producteur requis'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            sub_order = SubOrder.objects.get(
                id=pk,
                producer_id=producer_id
=======
        try:
            sub_order = SubOrder.objects.get(
                id=pk,
                producer_id=request.user.producer_profile.id
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            )
            
            order_item = OrderItem.objects.get(id=item_id, sub_order=sub_order)
            
            # Vérifier que c'est un produit au poids
            if order_item.sale_type != 'weight':
                return Response({
                    'error': 'Seuls les produits au poids peuvent être ajustés'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = AdjustOrderItemQuantitySerializer(
                data=request.data,
                context={'item': order_item}
            )
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour la quantité réelle
            order_item.quantity_actual = serializer.validated_data['quantity_actual']
            order_item.save()
            
            # Recalculer le subtotal de la sous-commande
            sub_order.update_subtotal()
            
            # Recalculer le total de la commande parent
            sub_order.parent_order.update_total()
            
            return Response({
                'message': 'Quantité ajustée',
                'adjustment': float(order_item.get_price_adjustment()),
                'sub_order': SubOrderSerializer(sub_order).data
            })
        
        except SubOrder.DoesNotExist:
            return Response({
                'error': 'Commande introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except OrderItem.DoesNotExist:
            return Response({
                'error': 'Item introuvable'
            }, status=status.HTTP_404_NOT_FOUND)