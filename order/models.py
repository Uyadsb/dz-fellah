from django.db import models
from decimal import Decimal


class Order(models.Model):
    """
    Commande Parent - Vue globale pour le client.
    Une commande parent contient plusieurs sous-commandes (une par producteur).
    """
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Client qui a passé la commande
    client_id = models.IntegerField(
        help_text="ID du client (référence à la table users)"
    )
    
    # Numéro de commande unique (généré automatiquement)
    order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Numéro unique de commande (ex: DZF-20231215-001)"
    )
    
    # Statut global de la commande
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Montant total de la commande
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Informations de livraison/retrait
    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('pickup_producer', 'Retrait chez producteur'),
            ('pickup_point', 'Retrait en point de collecte'),
        ],
        default='pickup_producer'
    )
    
    delivery_address = models.TextField(
        null=True,
        blank=True,
        help_text="Adresse de livraison ou point de collecte"
    )
    
    # Notes du client
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Instructions spéciales du client"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client_id', '-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - Client {self.client_id}"
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le numéro de commande."""
        if not self.order_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            # Compte les commandes du jour
            today_orders = Order.objects.filter(
                order_number__startswith=f'DZF-{date_str}'
            ).count()
            self.order_number = f'DZF-{date_str}-{today_orders + 1:04d}'
        super().save(*args, **kwargs)
    
    def get_sub_orders_count(self):
        """Nombre de sous-commandes (producteurs différents)."""
        return self.sub_orders.count()
    
    def update_total(self):
        """Recalcule le total depuis les sous-commandes."""
        total = Decimal('0.00')
        for sub_order in self.sub_orders.all():
            total += sub_order.get_total()
        self.total_amount = total
        self.save()
        return total
    
    def update_global_status(self):
        """
        Met à jour le statut global basé sur les sous-commandes.
        Logique: La commande est 'completed' si toutes les sous-commandes le sont.
        """
        sub_orders = self.sub_orders.all()
        if not sub_orders:
            return
        
        all_statuses = [so.status for so in sub_orders]
        
        if all(s == 'completed' for s in all_statuses):
            self.status = 'completed'
        elif all(s == 'cancelled' for s in all_statuses):
            self.status = 'cancelled'
        elif any(s == 'preparing' for s in all_statuses):
            self.status = 'preparing'
        elif all(s == 'ready' for s in all_statuses):
            self.status = 'ready'
        else:
            self.status = 'confirmed'
        
        self.save()


class SubOrder(models.Model):
    """
    Sous-Commande - Vue pour un producteur spécifique.
    Chaque producteur ne voit que sa sous-commande.
    """
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Lien vers la commande parent
    parent_order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='sub_orders'
    )
    
    # Producteur concerné
    producer_id = models.IntegerField(
        help_text="ID du producteur (référence à la table producers)"
    )
    
    # Numéro de sous-commande
    sub_order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Numéro de sous-commande (ex: DZF-20231215-001-P1)"
    )
    
    # Statut de cette sous-commande
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Montant de cette sous-commande
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Notes du producteur
    producer_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Notes du producteur (ex: ajustement de poids)"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sub_orders'
        verbose_name = 'Sous-commande'
        verbose_name_plural = 'Sous-commandes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['producer_id', '-created_at']),
            models.Index(fields=['parent_order', 'producer_id']),
            models.Index(fields=['sub_order_number']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['parent_order', 'producer_id'],
                name='unique_producer_per_order'
            )
        ]
    
    def __str__(self):
        return f"SubOrder {self.sub_order_number} - Producer {self.producer_id}"
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le numéro de sous-commande."""
        if not self.sub_order_number:
            # Compte les sous-commandes pour cette commande parent
            sub_count = SubOrder.objects.filter(
                parent_order=self.parent_order
            ).count()
            self.sub_order_number = f'{self.parent_order.order_number}-P{sub_count + 1}'
        super().save(*args, **kwargs)
    
    def get_total(self):
        """Calcule le total de cette sous-commande."""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.get_subtotal()
        return total
    
    def update_subtotal(self):
        """Recalcule et met à jour le subtotal."""
        self.subtotal = self.get_total()
        self.save()
        return self.subtotal


class OrderItem(models.Model):
    """
    Item de commande - Produit commandé avec quantité et prix.
    """
    
    # Lien vers la sous-commande
    sub_order = models.ForeignKey(
        SubOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Produit commandé
    product_id = models.IntegerField(
        help_text="ID du produit (référence à la table products)"
    )
    
    # Nom du produit au moment de la commande (snapshot)
    product_name = models.CharField(
        max_length=255,
        help_text="Nom du produit au moment de la commande"
    )
    
    # Quantité commandée
    quantity_ordered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantité commandée (unités ou kg)"
    )
    
    # Quantité réelle (peut être ajustée par le producteur pour les produits au poids)
    quantity_actual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Quantité réelle après préparation (pour produits au poids)"
    )
    
    # Prix unitaire au moment de la commande
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix unitaire au moment de la commande"
    )
    
    # Type de vente (pour référence)
    sale_type = models.CharField(
        max_length=20,
        choices=[('unit', 'Unité'), ('weight', 'Poids')],
        help_text="Type de vente du produit"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Item de commande'
        verbose_name_plural = 'Items de commande'
        indexes = [
            models.Index(fields=['sub_order', 'product_id']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"OrderItem {self.id} - {self.product_name} x {self.quantity_ordered}"
    
    def get_subtotal(self):
        """Calcule le sous-total de cet item."""
        # Utilise la quantité réelle si disponible, sinon la quantité commandée
        quantity = self.quantity_actual if self.quantity_actual else self.quantity_ordered
        return self.unit_price * quantity
    
    def get_price_adjustment(self):
        """
        Calcule l'ajustement de prix (si quantité réelle != quantité commandée).
        Retourne 0 si pas d'ajustement.
        """
        if not self.quantity_actual or self.quantity_actual == self.quantity_ordered:
            return Decimal('0.00')
        
        original_total = self.unit_price * self.quantity_ordered
        actual_total = self.unit_price * self.quantity_actual
        return actual_total - original_total