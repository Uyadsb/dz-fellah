"""
Django management command to clear demo data from DZ-Fellah.
Place this file in: config/management/commands/clear_demo_data.py

Usage:
    python manage.py clear_demo_data
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Clear all demo data from DZ-Fellah database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['yes']:
            confirm = input(
                '\n⚠️  This will DELETE ALL DATA from the database!\n'
                'Are you sure? Type "yes" to confirm: '
            )
            
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.WARNING('\n❌ Operation cancelled.\n'))
                return
        
        self.stdout.write(self.style.WARNING('\n🗑️  Clearing all data...\n'))
        
        try:
            with connection.cursor() as cursor:
                # Disable foreign key checks temporarily
                cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
                
                # Get counts before deletion
                cursor.execute("SELECT COUNT(*) FROM products")
                product_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM producers")
                producer_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM clients")
                client_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM carts")
                cart_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM orders")
                order_count = cursor.fetchone()[0]
                
                # Delete data in correct order (respecting foreign keys)
                self.stdout.write('Deleting order items...')
                cursor.execute("DELETE FROM order_items")
                
                self.stdout.write('Deleting sub-orders...')
                cursor.execute("DELETE FROM sub_orders")
                
                self.stdout.write('Deleting orders...')
                cursor.execute("DELETE FROM orders")
                
                self.stdout.write('Deleting cart items...')
                cursor.execute("DELETE FROM cart_items")
                
                self.stdout.write('Deleting carts...')
                cursor.execute("DELETE FROM carts")
                
                self.stdout.write('Deleting products...')
                cursor.execute("DELETE FROM products")
                
                self.stdout.write('Deleting producers...')
                cursor.execute("DELETE FROM producers")
                
                self.stdout.write('Deleting clients...')
                cursor.execute("DELETE FROM clients")
                
                self.stdout.write('Deleting users...')
                cursor.execute("DELETE FROM users")
                
                # Reset sequences
                self.stdout.write('Resetting ID sequences...')
                cursor.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE producers_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE clients_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE carts_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE cart_items_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE orders_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE sub_orders_id_seq RESTART WITH 1")
                cursor.execute("ALTER SEQUENCE order_items_id_seq RESTART WITH 1")
                
                # Re-enable foreign key checks
                cursor.execute("SET CONSTRAINTS ALL IMMEDIATE;")
            
            self.stdout.write(self.style.SUCCESS('\n✅ Data cleared successfully!\n'))
            self.stdout.write(self.style.SUCCESS('📊 Deleted:'))
            self.stdout.write(f'  • {order_count} orders')
            self.stdout.write(f'  • {cart_count} carts')
            self.stdout.write(f'  • {product_count} products')
            self.stdout.write(f'  • {producer_count} producers')
            self.stdout.write(f'  • {client_count} clients\n')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error clearing data: {str(e)}\n'))
            raise