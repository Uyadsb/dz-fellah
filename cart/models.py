from django.db import models
from decimal import Decimal


class Cart(models.Model):
    """
    Panier d'achat pour un client.
    Un client a un seul panier actif à la fois.
    """
    # On utilise user_id comme integer pour rester compatible avec le système SQL
    user_id = models.IntegerField(
        help_text="ID de l'utilisateur (référence à la table users)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        # Un seul panier actif par utilisateur
        constraints = [
            models.UniqueConstraint(
                fields=['user_id'],
                name='unique_active_cart_per_user'
            )
        ]
    
    def __str__(self):
        return f"Cart {self.id} - User {self.user_id}"
    
    def get_total(self):
        """Calcule le total du panier."""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.get_subtotal()
        return total
    
    def get_items_count(self):
        """Nombre total d'items dans le panier."""
        return self.items.count()
    
    def get_items_by_producer(self):
        """
        Groupe les items par producteur pour faciliter la création des sous-commandes.
        Retourne un dictionnaire : {producer_id: [items]}
        """
        items_by_producer = {}
        for item in self.items.select_related('product__producer').all():
            producer_id = item.product_id  # On récupère via SQL queries
            if producer_id not in items_by_producer:
                items_by_producer[producer_id] = []
            items_by_producer[producer_id].append(item)
        return items_by_producer


class CartItem(models.Model):
    """
    Item dans le panier.
    Représente un produit avec sa quantité.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Référence au produit via son ID (compatible avec le système SQL)
    product_id = models.IntegerField(
        help_text="ID du produit (référence à la table products)"
    )
    
    # Quantité commandée
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantité (unités ou kg selon le type de vente)"
    )
    
    # Prix unitaire au moment de l'ajout au panier (snapshot)
    # Important pour éviter les surprises si le prix change
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix unitaire au moment de l'ajout au panier"
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Item du panier'
        verbose_name_plural = 'Items du panier'
        # Un produit ne peut être qu'une seule fois dans un panier
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product_id'],
                name='unique_product_per_cart'
            )
        ]
        indexes = [
            models.Index(fields=['cart', 'product_id']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"CartItem {self.id} - Product {self.product_id} x {self.quantity}"
    
    def get_subtotal(self):
        """Calcule le sous-total pour cet item."""
        return self.price_snapshot * self.quantity
    
    def get_product_details(self):
        """
        Récupère les détails du produit depuis la base de données.
        Utilise les queries SQL existantes.
        """
        from products import queries as product_queries
        return product_queries.get_product_detail(self.product_id)
    
    def update_quantity(self, new_quantity):
        """
        Met à jour la quantité avec validation du stock.
        """
        if new_quantity <= 0:
            raise ValueError("La quantité doit être supérieure à 0")
        
        # Vérifier le stock disponible
        product = self.get_product_details()
        if not product:
            raise ValueError("Produit introuvable")
        
        if new_quantity > product['stock']:
            raise ValueError(f"Stock insuffisant. Disponible : {product['stock']}")
        
        self.quantity = new_quantity
        self.save()
        return self