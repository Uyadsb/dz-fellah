from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)
from users.authentication import CustomJWTAuthentication
from users.permissions import CanBuyProducts


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer le panier d'achat.
    """
    
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated, CanBuyProducts]
    
    def get_or_create_cart(self, user_id):
        """Récupère ou crée le panier de l'utilisateur."""
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        return cart
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """
        GET /api/cart/my_cart/
        Récupère le panier de l'utilisateur connecté.
        """
        cart = self.get_or_create_cart(request.user.id)
        serializer = CartSerializer(cart)
        
        return Response({
            'message': 'Votre panier',
            'cart': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        POST /api/cart/add_item/
        Ajoute un produit au panier.
        
        Body:
        {
            "product_id": 1,
            "quantity": 2.5
        }
        """
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        # Récupérer le produit
        from products import queries as product_queries
        product = product_queries.get_product_detail(product_id)
        
        if not product:
            return Response({
                'error': 'Produit introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier le stock
        if quantity > product['stock']:
            return Response({
                'error': f"Stock insuffisant. Disponible : {product['stock']}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Récupérer ou créer le panier
                cart = self.get_or_create_cart(request.user.id)
                
                # Vérifier si le produit est déjà dans le panier
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product_id=product_id,
                    defaults={
                        'quantity': quantity,
                        'price_snapshot': product['price']
                    }
                )
                
                if not created:
                    # Produit déjà dans le panier : mettre à jour la quantité
                    new_quantity = cart_item.quantity + quantity
                    
                    if new_quantity > product['stock']:
                        return Response({
                            'error': f"Stock insuffisant. Vous avez déjà {cart_item.quantity} "
                                   f"dans votre panier. Stock disponible : {product['stock']}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    message = f"Quantité mise à jour : {cart_item.quantity}"
                else:
                    message = "Produit ajouté au panier"
                
                # Retourner le panier mis à jour
                cart_serializer = CartSerializer(cart)
                
                return Response({
                    'message': message,
                    'cart': cart_serializer.data,
                    'item': CartItemSerializer(cart_item).data
                }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': f'Erreur lors de l\'ajout au panier : {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['patch'], url_path='update_item/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        PATCH /api/cart/update_item/{item_id}/
        Met à jour la quantité d'un item dans le panier.
        
        Body:
        {
            "quantity": 3.0
        }
        """
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Récupérer le panier de l'utilisateur
            cart = self.get_or_create_cart(request.user.id)
            
            # Récupérer l'item
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            # Mettre à jour la quantité avec validation du stock
            new_quantity = serializer.validated_data['quantity']
            cart_item.update_quantity(new_quantity)
            
            # Retourner le panier mis à jour
            cart_serializer = CartSerializer(cart)
            
            return Response({
                'message': 'Quantité mise à jour',
                'cart': cart_serializer.data,
                'item': CartItemSerializer(cart_item).data
            })
        
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Item non trouvé dans votre panier'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la mise à jour : {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """
        DELETE /api/cart/remove_item/{item_id}/
        Supprime un item du panier.
        """
        try:
            # Récupérer le panier de l'utilisateur
            cart = self.get_or_create_cart(request.user.id)
            
            # Récupérer et supprimer l'item
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            # Retourner le panier mis à jour
            cart_serializer = CartSerializer(cart)
            
            return Response({
                'message': 'Produit retiré du panier',
                'cart': cart_serializer.data
            })
        
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Item non trouvé dans votre panier'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'error': f'Erreur lors de la suppression : {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):
        """
        DELETE /api/cart/clear_cart/
        Vide complètement le panier.
        """
        try:
            cart = self.get_or_create_cart(request.user.id)
            cart.items.all().delete()
            
            return Response({
                'message': 'Panier vidé',
                'cart': CartSerializer(cart).data
            })
        
        except Exception as e:
            return Response({
                'error': f'Erreur lors du vidage du panier : {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def validate_cart(self, request):
        """
        GET /api/cart/validate_cart/
        Vérifie que tous les produits du panier sont disponibles.
        Utile avant de passer commande.
        """
        cart = self.get_or_create_cart(request.user.id)
        
        if not cart.items.exists():
            return Response({
                'valid': False,
                'error': 'Votre panier est vide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        errors = []
        warnings = []
        
        from products import queries as product_queries
        
        for item in cart.items.all():
            product = product_queries.get_product_detail(item.product_id)
            
            if not product:
                errors.append({
                    'item_id': item.id,
                    'product_id': item.product_id,
                    'error': 'Produit introuvable'
                })
                continue
            
            # Vérifier le stock
            if item.quantity > product['stock']:
                errors.append({
                    'item_id': item.id,
                    'product_name': product['name'],
                    'quantity_requested': float(item.quantity),
                    'stock_available': float(product['stock']),
                    'error': f"Stock insuffisant. Disponible : {product['stock']}"
                })
            
            # Vérifier si le prix a changé
            if item.price_snapshot != product['price']:
                price_diff = product['price'] - item.price_snapshot
                warnings.append({
                    'item_id': item.id,
                    'product_name': product['name'],
                    'old_price': float(item.price_snapshot),
                    'new_price': float(product['price']),
                    'difference': float(price_diff),
                    'warning': f"Le prix a changé de {price_diff:+.2f} DA"
                })
        
        if errors:
            return Response({
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'valid': True,
            'warnings': warnings,
            'message': 'Votre panier est prêt pour la commande',
            'cart': CartSerializer(cart).data
        })