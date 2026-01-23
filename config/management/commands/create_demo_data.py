"""
Django management command to create demo data for DZ-Fellah MVP.
Place this file in: config/management/commands/create_demo_data.py

Usage:
    python manage.py create_demo_data
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.hashers import make_password
from datetime import date, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create demo data for DZ-Fellah MVP testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🌱 Creating demo data for DZ-Fellah...\n'))
        
        try:
            # Create demo data
            self.create_producers()
            self.create_clients()
            self.create_products()
            
            self.stdout.write(self.style.SUCCESS('\n✅ Demo data created successfully!\n'))
            self.print_summary()
            self.print_login_credentials()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error creating demo data: {str(e)}\n'))
            raise

    def create_producers(self):
        """Create demo producer accounts."""
        self.stdout.write('Creating producers...')
        
        producers_data = [
            {
                'email': 'ferme.alger@example.com',
                'password': 'Producer123',
                'first_name': 'Ahmed',
                'last_name': 'Benali',
                'phone': '0551234567',
                'shop_name': 'Ferme Bio Alger',
                'description': 'Production biologique de légumes frais dans la région d\'Alger. Certifiée agriculture biologique.',
                'address': '15 Route de Zéralda',
                'city': 'Zéralda',
                'wilaya': 'Alger',
                'methods': 'Agriculture biologique, sans pesticides',
                'is_bio_certified': True
            },
            {
                'email': 'jardins.oran@example.com',
                'password': 'Producer123',
                'first_name': 'Fatima',
                'last_name': 'Meziane',
                'phone': '0661234567',
                'shop_name': 'Les Jardins d\'Oran',
                'description': 'Fruits et légumes de saison cultivés en agriculture raisonnée.',
                'address': 'Zone agricole de Misserghin',
                'city': 'Oran',
                'wilaya': 'Oran',
                'methods': 'Agriculture raisonnée',
                'is_bio_certified': False
            },
            {
                'email': 'miel.tlemcen@example.com',
                'password': 'Producer123',
                'first_name': 'Karim',
                'last_name': 'Tounsi',
                'phone': '0771234567',
                'shop_name': 'Miel & Nature Tlemcen',
                'description': 'Production artisanale de miel et produits de la ruche de haute qualité.',
                'address': 'Douar Ouled Ali',
                'city': 'Tlemcen',
                'wilaya': 'Tlemcen',
                'methods': 'Apiculture traditionnelle',
                'is_bio_certified': True
            },
            {
                'email': 'ferme.constantine@example.com',
                'password': 'Producer123',
                'first_name': 'Leila',
                'last_name': 'Mansouri',
                'phone': '0551234568',
                'shop_name': 'Ferme des Oliviers',
                'description': 'Huile d\'olive extra vierge et olives de table de qualité supérieure.',
                'address': 'Route de Hamma Bouziane',
                'city': 'Constantine',
                'wilaya': 'Constantine',
                'methods': 'Agriculture familiale traditionnelle',
                'is_bio_certified': False
            },
            {
                'email': 'jardin.blida@example.com',
                'password': 'Producer123',
                'first_name': 'Youcef',
                'last_name': 'Hadj',
                'phone': '0661234568',
                'shop_name': 'Jardin de la Mitidja',
                'description': 'Agrumes et fruits de saison de la plaine de la Mitidja.',
                'address': 'Ouled Yaïch',
                'city': 'Blida',
                'wilaya': 'Blida',
                'methods': 'Agriculture durable',
                'is_bio_certified': True
            }
        ]
        
        with connection.cursor() as cursor:
            for prod in producers_data:
                # Hash password using Django's hasher
                hashed_password = make_password(prod['password'])
                
                # Create user
                cursor.execute("""
                    INSERT INTO users (email, password, user_type, first_name, last_name, phone, is_active, is_verified)
                    VALUES (%s, %s, 'producer', %s, %s, %s, TRUE, TRUE)
                    RETURNING id
                """, [
                    prod['email'],
                    hashed_password,
                    prod['first_name'],
                    prod['last_name'],
                    prod['phone']
                ])
                user_id = cursor.fetchone()[0]
                
                # Create producer profile
                cursor.execute("""
                    INSERT INTO producers (user_id, shop_name, description, address, city, wilaya, methods, is_bio_certified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    user_id,
                    prod['shop_name'],
                    prod['description'],
                    prod['address'],
                    prod['city'],
                    prod['wilaya'],
                    prod['methods'],
                    prod['is_bio_certified']
                ])
                
                self.stdout.write(f'  ✓ Created producer: {prod["shop_name"]}')

    def create_clients(self):
        """Create demo client accounts."""
        self.stdout.write('\nCreating clients...')
        
        clients_data = [
            {
                'email': 'client1@example.com',
                'password': 'Client123',
                'first_name': 'Sarah',
                'last_name': 'Djaballah',
                'phone': '0551234569',
                'address': 'Cité 500 logements',
                'city': 'Alger',
                'wilaya': 'Alger'
            },
            {
                'email': 'client2@example.com',
                'password': 'Client123',
                'first_name': 'Mohamed',
                'last_name': 'Bensalem',
                'phone': '0661234569',
                'address': 'Résidence El Yasmine',
                'city': 'Oran',
                'wilaya': 'Oran'
            },
            {
                'email': 'client3@example.com',
                'password': 'Client123',
                'first_name': 'Amina',
                'last_name': 'Khelifi',
                'phone': '0771234569',
                'address': 'Cité Daksi',
                'city': 'Constantine',
                'wilaya': 'Constantine'
            }
        ]
        
        with connection.cursor() as cursor:
            for client in clients_data:
                # Hash password using Django's hasher
                hashed_password = make_password(client['password'])
                
                # Create user
                cursor.execute("""
                    INSERT INTO users (email, password, user_type, first_name, last_name, phone, is_active, is_verified)
                    VALUES (%s, %s, 'client', %s, %s, %s, TRUE, TRUE)
                    RETURNING id
                """, [
                    client['email'],
                    hashed_password,
                    client['first_name'],
                    client['last_name'],
                    client['phone']
                ])
                user_id = cursor.fetchone()[0]
                
                # Create client profile
                cursor.execute("""
                    INSERT INTO clients (user_id, address, city, wilaya)
                    VALUES (%s, %s, %s, %s)
                """, [
                    user_id,
                    client['address'],
                    client['city'],
                    client['wilaya']
                ])
                
                self.stdout.write(f'  ✓ Created client: {client["first_name"]} {client["last_name"]}')

    def create_products(self):
        """Create demo products for each producer."""
        self.stdout.write('\nCreating products...')
        
        with connection.cursor() as cursor:
            # Get producer IDs
            cursor.execute("SELECT id, shop_name FROM producers ORDER BY id")
            producers = cursor.fetchall()
            
            for producer_id, shop_name in producers:
                products = self.get_products_for_producer(shop_name)
                
                for product in products:
                    cursor.execute("""
                        INSERT INTO products (
                            producer_id, name, description, sale_type, price, stock,
                            product_type, harvest_date, is_anti_gaspi
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        producer_id,
                        product['name'],
                        product['description'],
                        product['sale_type'],
                        product['price'],
                        product['stock'],
                        product['product_type'],
                        product['harvest_date'],
                        product['is_anti_gaspi']
                    ])
                
                self.stdout.write(f'  ✓ Created {len(products)} products for {shop_name}')

    def get_products_for_producer(self, shop_name):
        """Get appropriate products based on producer name."""
        today = date.today()
        
        if 'Ferme Bio Alger' in shop_name:
            return [
                {
                    'name': 'Tomates Bio',
                    'description': 'Tomates cultivées sans pesticides, goût authentique',
                    'sale_type': 'weight',
                    'price': Decimal('280.00'),
                    'stock': Decimal('50.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=1),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Carottes Bio',
                    'description': 'Carottes croquantes et sucrées',
                    'sale_type': 'weight',
                    'price': Decimal('180.00'),
                    'stock': Decimal('35.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=2),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Salade Bio',
                    'description': 'Salade verte fraîche du jour',
                    'sale_type': 'unit',
                    'price': Decimal('50.00'),
                    'stock': Decimal('30.00'),
                    'product_type': 'fresh',
                    'harvest_date': today,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Courgettes Bio (Anti-gaspi)',
                    'description': 'Courgettes parfaites pour la cuisine, petit calibre - Prix réduit!',
                    'sale_type': 'weight',
                    'price': Decimal('100.00'),
                    'stock': Decimal('20.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=3),
                    'is_anti_gaspi': True
                },
                {
                    'name': 'Poivrons Bio',
                    'description': 'Poivrons colorés, riches en vitamines',
                    'sale_type': 'weight',
                    'price': Decimal('320.00'),
                    'stock': Decimal('25.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=1),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Aubergines Bio',
                    'description': 'Aubergines tendres et savoureuses',
                    'sale_type': 'weight',
                    'price': Decimal('200.00'),
                    'stock': Decimal('30.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=1),
                    'is_anti_gaspi': False
                }
            ]
        
        elif 'Jardins d\'Oran' in shop_name:
            return [
                {
                    'name': 'Oranges de Saison',
                    'description': 'Oranges juteuses et sucrées',
                    'sale_type': 'weight',
                    'price': Decimal('150.00'),
                    'stock': Decimal('100.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=5),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Pommes de Terre',
                    'description': 'Pommes de terre de qualité, idéales pour toutes préparations',
                    'sale_type': 'weight',
                    'price': Decimal('120.00'),
                    'stock': Decimal('200.00'),
                    'product_type': 'other',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Fraises',
                    'description': 'Fraises parfumées et gourmandes',
                    'sale_type': 'weight',
                    'price': Decimal('450.00'),
                    'stock': Decimal('15.00'),
                    'product_type': 'fresh',
                    'harvest_date': today,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Concombres',
                    'description': 'Concombres croquants et rafraîchissants',
                    'sale_type': 'unit',
                    'price': Decimal('40.00'),
                    'stock': Decimal('50.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=1),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Bananes (Anti-gaspi)',
                    'description': 'Bananes très mûres, parfaites pour smoothies - Prix réduit!',
                    'sale_type': 'weight',
                    'price': Decimal('120.00'),
                    'stock': Decimal('10.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=4),
                    'is_anti_gaspi': True
                }
            ]
        
        elif 'Miel & Nature' in shop_name:
            return [
                {
                    'name': 'Miel de Montagne',
                    'description': 'Miel pur de montagne, récolte 2024',
                    'sale_type': 'unit',
                    'price': Decimal('1200.00'),
                    'stock': Decimal('50.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Miel d\'Eucalyptus',
                    'description': 'Miel d\'eucalyptus aux propriétés médicinales',
                    'sale_type': 'unit',
                    'price': Decimal('1400.00'),
                    'stock': Decimal('30.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Miel d\'Oranger',
                    'description': 'Miel doux et parfumé d\'oranger',
                    'sale_type': 'unit',
                    'price': Decimal('1300.00'),
                    'stock': Decimal('40.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Pollen Frais',
                    'description': 'Pollen frais congelé, riche en nutriments',
                    'sale_type': 'unit',
                    'price': Decimal('800.00'),
                    'stock': Decimal('20.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                }
            ]
        
        elif 'Ferme des Oliviers' in shop_name:
            return [
                {
                    'name': 'Huile d\'Olive Extra Vierge 1L',
                    'description': 'Première pression à froid, acidité < 0.5%',
                    'sale_type': 'unit',
                    'price': Decimal('1800.00'),
                    'stock': Decimal('100.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Olives de Table Vertes',
                    'description': 'Olives vertes marinées maison',
                    'sale_type': 'weight',
                    'price': Decimal('400.00'),
                    'stock': Decimal('50.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Olives Noires',
                    'description': 'Olives noires séchées au soleil',
                    'sale_type': 'weight',
                    'price': Decimal('450.00'),
                    'stock': Decimal('40.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Huile d\'Olive Parfumée au Thym',
                    'description': 'Huile d\'olive macérée avec thym sauvage',
                    'sale_type': 'unit',
                    'price': Decimal('2200.00'),
                    'stock': Decimal('30.00'),
                    'product_type': 'processed',
                    'harvest_date': None,
                    'is_anti_gaspi': False
                }
            ]
        
        elif 'Jardin de la Mitidja' in shop_name:
            return [
                {
                    'name': 'Citrons',
                    'description': 'Citrons juteux et parfumés',
                    'sale_type': 'weight',
                    'price': Decimal('200.00'),
                    'stock': Decimal('60.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=3),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Mandarines',
                    'description': 'Mandarines douces et faciles à éplucher',
                    'sale_type': 'weight',
                    'price': Decimal('220.00'),
                    'stock': Decimal('80.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=2),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Pommes Golden',
                    'description': 'Pommes croquantes et sucrées',
                    'sale_type': 'weight',
                    'price': Decimal('280.00'),
                    'stock': Decimal('70.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=10),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Poires',
                    'description': 'Poires juteuses et fondantes',
                    'sale_type': 'weight',
                    'price': Decimal('320.00'),
                    'stock': Decimal('40.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=8),
                    'is_anti_gaspi': False
                },
                {
                    'name': 'Oranges Bio (Anti-gaspi)',
                    'description': 'Oranges avec légères imperfections, goût excellent - Prix réduit!',
                    'sale_type': 'weight',
                    'price': Decimal('100.00'),
                    'stock': Decimal('30.00'),
                    'product_type': 'fresh',
                    'harvest_date': today - timedelta(days=5),
                    'is_anti_gaspi': True
                }
            ]
        
        return []

    def print_summary(self):
        """Print summary of created data."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='producer'")
            producer_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='client'")
            client_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE is_anti_gaspi=TRUE")
            anti_gaspi_count = cursor.fetchone()[0]
        
        self.stdout.write(self.style.SUCCESS('\n📊 Summary:'))
        self.stdout.write(f'  • Producers: {producer_count}')
        self.stdout.write(f'  • Clients: {client_count}')
        self.stdout.write(f'  • Products: {product_count}')
        self.stdout.write(f'  • Anti-gaspi products: {anti_gaspi_count}')

    def print_login_credentials(self):
        """Print login credentials for testing."""
        self.stdout.write(self.style.SUCCESS('\n🔑 Login Credentials:\n'))
        
        self.stdout.write(self.style.WARNING('Producers:'))
        producers = [
            ('ferme.alger@example.com', 'Ferme Bio Alger'),
            ('jardins.oran@example.com', 'Les Jardins d\'Oran'),
            ('miel.tlemcen@example.com', 'Miel & Nature Tlemcen'),
            ('ferme.constantine@example.com', 'Ferme des Oliviers'),
            ('jardin.blida@example.com', 'Jardin de la Mitidja'),
        ]
        
        for email, name in producers:
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Password: Producer123')
            self.stdout.write(f'  Shop: {name}\n')
        
        self.stdout.write(self.style.WARNING('Clients:'))
        clients = [
            ('client1@example.com', 'Sarah Djaballah'),
            ('client2@example.com', 'Mohamed Bensalem'),
            ('client3@example.com', 'Amina Khelifi'),
        ]
        
        for email, name in clients:
            self.stdout.write(f'  Email: {email}')
            self.stdout.write(f'  Password: Client123')
            self.stdout.write(f'  Name: {name}\n')