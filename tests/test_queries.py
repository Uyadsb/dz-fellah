import pytest
from datetime import date, timedelta
from decimal import Decimal
from db import users_queries, products_queries


# ============================================
# USER QUERIES TESTS
# ============================================

@pytest.mark.django_db
class TestUserQueries:
    """Test user-related database queries."""
    
    def test_create_user_success(self):
        """Test creating a new user successfully."""
        user = users_queries.create_user(
            email='test@example.com',
            password='TestPass123',
            user_type='producer',
            first_name='Test',
            last_name='User',
            phone='0555123456'
        )
        
        assert user is not None
        assert user['email'] == 'test@example.com'
        assert user['user_type'] == 'producer'
        assert user['first_name'] == 'Test'
        assert user['last_name'] == 'User'
        assert user['phone'] == '0555123456'
        assert user['is_active'] is True
        assert user['is_verified'] is False
        assert 'id' in user
        assert 'created_at' in user
    
    def test_create_user_duplicate_email(self):
        """Test that duplicate email is detected."""
        # Create first user
        users_queries.create_user(
            email='duplicate@example.com',
            password='Pass123',
            user_type='client',
            first_name='First',
            last_name='User'
        )
        
        # Check email exists
        assert users_queries.email_exists('duplicate@example.com') is True
    
    def test_create_producer_profile_success(self):
        """Test creating a producer profile."""
        # Create user first
        user = users_queries.create_user(
            email='producer@example.com',
            password='Pass123',
            user_type='producer',
            first_name='Producer',
            last_name='User'
        )
        
        # Create producer profile
        profile = users_queries.create_producer_profile(
            user_id=user['id'],
            shop_name='Test Farm',
            description='Organic vegetables',
            address='123 Farm Road',
            city='Alger',
            wilaya='Alger',
            methods='Organic farming',
            is_bio_certified=True
        )
        
        assert profile is not None
        assert profile['user_id'] == user['id']
        assert profile['shop_name'] == 'Test Farm'
        assert profile['description'] == 'Organic vegetables'
        assert profile['city'] == 'Alger'
        assert profile['is_bio_certified'] is True
    
    def test_create_producer_profile_minimal_fields(self):
        """Test creating producer profile with only required fields."""
        user = users_queries.create_user(
            email='minimal@example.com',
            password='Pass123',
            user_type='producer',
            first_name='Minimal',
            last_name='User'
        )
        
        profile = users_queries.create_producer_profile(
            user_id=user['id'],
            shop_name='Minimal Farm'
        )
        
        assert profile is not None
        assert profile['shop_name'] == 'Minimal Farm'
        assert profile['description'] is None
        assert profile['is_bio_certified'] is False
    
    def test_get_user_by_email_with_producer_profile(self):
        """Test retrieving user with producer profile in single query."""
        # Create user and profile
        user = users_queries.create_user(
            email='getuser@example.com',
            password='Pass123',
            user_type='producer',
            first_name='Get',
            last_name='User'
        )
        
        users_queries.create_producer_profile(
            user_id=user['id'],
            shop_name='Get User Farm',
            city='Oran'
        )
        
        # Retrieve user
        result = users_queries.get_user_by_email('getuser@example.com')
        
        assert result is not None
        assert result['email'] == 'getuser@example.com'
        assert result['producer_id'] is not None
        assert result['shop_name'] == 'Get User Farm'
        assert result['producer_city'] == 'Oran'
        assert result['client_id'] is None  # Not a client
    
    def test_get_user_by_email_not_found(self):
        """Test retrieving non-existent user returns None."""
        result = users_queries.get_user_by_email('nonexistent@example.com')
        assert result is None
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        user = users_queries.create_user(
            email='password@example.com',
            password='CorrectPass123',
            user_type='client',
            first_name='Pass',
            last_name='Test'
        )
        
        # Get user with password
        user_data = users_queries.get_user_by_email('password@example.com')
        
        # Verify correct password
        assert users_queries.verify_password(
            user_data['password'],
            'CorrectPass123'
        ) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        user = users_queries.create_user(
            email='wrongpass@example.com',
            password='CorrectPass123',
            user_type='client',
            first_name='Wrong',
            last_name='Pass'
        )
        
        user_data = users_queries.get_user_by_email('wrongpass@example.com')
        
        # Verify incorrect password
        assert users_queries.verify_password(
            user_data['password'],
            'WrongPassword'
        ) is False


# ============================================
# PRODUCT QUERIES TESTS
# ============================================

@pytest.mark.django_db
class TestProductQueries:
    """Test product-related database queries."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a producer for product tests."""
        user = users_queries.create_user(
            email='productproducer@example.com',
            password='Pass123',
            user_type='producer',
            first_name='Product',
            last_name='Producer'
        )
        
        self.producer = users_queries.create_producer_profile(
            user_id=user['id'],
            shop_name='Product Test Farm'
        )
    
    def test_create_product_full_fields(self):
        """Test creating product with all fields."""
        product = products_queries.create_product(
            producer_id=self.producer['id'],
            name='Fresh Tomatoes',
            description='Organic tomatoes from local farm',
            photo_url='http://example.com/tomato.jpg',
            sale_type='weight',
            price=Decimal('250.00'),
            stock=Decimal('50.00'),
            product_type='fresh',
            harvest_date=date.today(),
            is_anti_gaspi=False
        )
        
        assert product is not None
        assert product['name'] == 'Fresh Tomatoes'
        assert product['description'] == 'Organic tomatoes from local farm'
        assert product['sale_type'] == 'weight'
        assert product['price'] == Decimal('250.00')
        assert product['stock'] == Decimal('50.00')
        assert product['product_type'] == 'fresh'
        assert product['is_anti_gaspi'] is False
    
    def test_create_product_minimal_fields(self):
        """Test creating product with only required fields."""
        product = products_queries.create_product(
            producer_id=self.producer['id'],
            name='Honey Jar',
            description=None,
            photo_url=None,
            sale_type='unit',
            price=Decimal('800.00'),
            stock=Decimal('20.00'),
            product_type='processed',
            harvest_date=None,
            is_anti_gaspi=False
        )
        
        assert product is not None
        assert product['name'] == 'Honey Jar'
        assert product['description'] is None
        assert product['sale_type'] == 'unit'
        assert product['harvest_date'] is None
    
    def test_create_product_anti_gaspi(self):
        """Test creating anti-gaspi product."""
        product = products_queries.create_product(
            producer_id=self.producer['id'],
            name='Old Lettuce',
            description='Discounted lettuce',
            photo_url=None,
            sale_type='unit',
            price=Decimal('40.00'),
            stock=Decimal('10.00'),
            product_type='fresh',
            harvest_date=date.today() - timedelta(days=3),
            is_anti_gaspi=True
        )
        
        assert product is not None
        assert product['is_anti_gaspi'] is True
    
    def test_get_home_products_no_filters(self):
        """Test getting home products without filters."""
        # Create some products
        for i in range(3):
            products_queries.create_product(
                producer_id=self.producer['id'],
                name=f'Product {i}',
                description=None,
                photo_url=None,
                sale_type='unit',
                price=Decimal('100.00'),
                stock=Decimal('10.00'),
                product_type='fresh',
                harvest_date=date.today(),
                is_anti_gaspi=False
            )
        
        products = products_queries.get_home_products(limit=10)
        
        assert len(products) >= 3
        assert all('producer_name' in p for p in products)
        assert all('producer_id' in p for p in products)
    
    def test_get_home_products_filter_by_type(self):
        """Test filtering home products by type."""
        # Create fresh product
        products_queries.create_product(
            producer_id=self.producer['id'],
            name='Fresh Product',
            description=None,
            photo_url=None,
            sale_type='unit',
            price=Decimal('100.00'),
            stock=Decimal('10.00'),
            product_type='fresh',
            harvest_date=date.today(),
            is_anti_gaspi=False
        )
        
        # Create processed product
        products_queries.create_product(
            producer_id=self.producer['id'],
            name='Processed Product',
            description=None,
            photo_url=None,
            sale_type='unit',
            price=Decimal('150.00'),
            stock=Decimal('5.00'),
            product_type='processed',
            harvest_date=None,
            is_anti_gaspi=False
        )
        
        fresh_products = products_queries.get_home_products(
            product_type='fresh',
            limit=10
        )
        
        assert all(p['product_type'] == 'fresh' for p in fresh_products)
    
    def test_get_home_products_filter_by_anti_gaspi(self):
        """Test filtering home products by anti-gaspi status."""
        # Create anti-gaspi product
        products_queries.create_product(
            producer_id=self.producer['id'],
            name='Anti Gaspi Product',
            description=None,
            photo_url=None,
            sale_type='unit',
            price=Decimal('50.00'),
            stock=Decimal('10.00'),
            product_type='fresh',
            harvest_date=date.today() - timedelta(days=3),
            is_anti_gaspi=True
        )
        
        anti_gaspi_products = products_queries.get_home_products(
            is_anti_gaspi=True,
            limit=10
        )
        
        assert all(p['is_anti_gaspi'] is True for p in anti_gaspi_products)
    
    def test_get_home_products_limit(self):
        """Test that limit parameter works."""
        # Create 10 products
        for i in range(10):
            products_queries.create_product(
                producer_id=self.producer['id'],
                name=f'Limit Test {i}',
                description=None,
                photo_url=None,
                sale_type='unit',
                price=Decimal('100.00'),
                stock=Decimal('10.00'),
                product_type='fresh',
                harvest_date=date.today(),
                is_anti_gaspi=False
            )
        
        products = products_queries.get_home_products(limit=5)
        
        assert len(products) <= 5
    
    def test_get_home_products_includes_producer_info(self):
        """Test that products include producer info (no N+1)."""
        products_queries.create_product(
            producer_id=self.producer['id'],
            name='Test Producer Info',
            description=None,
            photo_url=None,
            sale_type='unit',
            price=Decimal('100.00'),
            stock=Decimal('10.00'),
            product_type='fresh',
            harvest_date=date.today(),
            is_anti_gaspi=False
        )
        
        products = products_queries.get_home_products(limit=1)
        
        assert len(products) > 0
        product = products[0]
        assert 'producer_id' in product
        assert 'producer_name' in product
        assert product['producer_name'] == 'Product Test Farm'


# ============================================
# INTEGRATION TESTS
# ============================================

@pytest.mark.django_db
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_producer_registration_flow(self):
        """Test complete producer registration and product creation."""
        # Step 1: Register producer
        user = users_queries.create_user(
            email='integration@example.com',
            password='IntegrationPass123',
            user_type='producer',
            first_name='Integration',
            last_name='Test',
            phone='0666123456'
        )
        
        producer = users_queries.create_producer_profile(
            user_id=user['id'],
            shop_name='Integration Farm',
            city='Constantine',
            wilaya='Constantine',
            is_bio_certified=True
        )
        
        # Step 2: Login simulation (get user by email)
        user_data = users_queries.get_user_by_email('integration@example.com')
        assert user_data is not None
        assert users_queries.verify_password(user_data['password'], 'IntegrationPass123')
        
        # Step 3: Create product
        product = products_queries.create_product(
            producer_id=producer['id'],
            name='Integration Product',
            description='Test product',
            photo_url=None,
            sale_type='weight',
            price=Decimal('300.00'),
            stock=Decimal('25.00'),
            product_type='fresh',
            harvest_date=date.today(),
            is_anti_gaspi=False
        )
        
        assert product is not None
        assert product['producer_id'] == producer['id']
        
        # Step 4: Verify product appears in listings
        products = products_queries.get_home_products(limit=100)
        product_names = [p['name'] for p in products]
        assert 'Integration Product' in product_names
    
    def test_search_and_filter_workflow(self):
        """Test searching and filtering products."""
        # Create producer
        user = users_queries.create_user(
            email='search@example.com',
            password='Pass123',
            user_type='producer',
            first_name='Search',
            last_name='Test'
        )
        
        producer = users_queries.create_producer_profile(
            user_id=user['id'],
            shop_name='Search Farm',
            wilaya='Oran'
        )
        
        # Create products with different attributes
        products_queries.create_product(
            producer_id=producer['id'],
            name='Red Tomatoes',
            description='Fresh red tomatoes',
            photo_url=None,
            sale_type='weight',
            price=Decimal('200.00'),
            stock=Decimal('30.00'),
            product_type='fresh',
            harvest_date=date.today(),
            is_anti_gaspi=False
        )
        
        products_queries.create_product(
            producer_id=producer['id'],
            name='Cherry Tomatoes',
            description='Small cherry tomatoes',
            photo_url=None,
            sale_type='weight',
            price=Decimal('350.00'),
            stock=Decimal('15.00'),
            product_type='fresh',
            harvest_date=date.today(),
            is_anti_gaspi=False
        )
        
        # Test search
        search_results = products_queries.search_products('tomatoes')
        assert len(search_results) >= 2
        assert all('tomatoes' in p['name'].lower() for p in search_results)
        
        # Test filter by wilaya
        filtered = products_queries.filter_products(wilaya='Oran')
        assert len(filtered) >= 2