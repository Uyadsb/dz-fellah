from django.db import connection
from datetime import datetime, timedelta


def dict_fetchall(cursor):
    """Convert cursor results to list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    """Convert single cursor result to dictionary."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# ============================================
# PUBLIC QUERIES (No authentication required)
# ============================================

def get_home_products(product_type=None, is_anti_gaspi=None, limit=20):
    """
    Get products for homepage with filters and random order.
    PostgreSQL: Uses RANDOM() for random ordering.
    """
    sql = """
        SELECT 
            p.id, p.name, p.photo_url, p.price, p.sale_type, p.stock,
            p.product_type, p.is_anti_gaspi, p.harvest_date,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE 1=1
    """
    params = []
    
    if product_type:
        sql += " AND p.product_type = %s"
        params.append(product_type)
    
    if is_anti_gaspi is not None:
        sql += " AND p.is_anti_gaspi = %s"
        params.append(is_anti_gaspi)
    
    sql += " ORDER BY RANDOM() LIMIT %s"
    params.append(limit)
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)


def search_products(query, product_type=None, is_anti_gaspi=None):
    """
    Search products by name or description.
    PostgreSQL: Uses ILIKE for case-insensitive search.
    """
    sql = """
        SELECT 
            p.id, p.name, p.photo_url, p.price, p.sale_type, p.stock,
            p.product_type, p.is_anti_gaspi, p.harvest_date,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE (p.name ILIKE %s OR p.description ILIKE %s)
    """
    params = [f'%{query}%', f'%{query}%']
    
    if product_type:
        sql += " AND p.product_type = %s"
        params.append(product_type)
    
    if is_anti_gaspi is not None:
        sql += " AND p.is_anti_gaspi = %s"
        params.append(is_anti_gaspi)
    
    sql += " ORDER BY p.created_at DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)


def get_producer_products(producer_id, product_type=None, is_anti_gaspi=None):
    """
    Get all products from a specific producer (public view).
    """
    sql = """
        SELECT 
            p.id, p.name, p.photo_url, p.price, p.sale_type, p.stock,
            p.product_type, p.is_anti_gaspi, p.harvest_date,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE p.producer_id = %s
    """
    params = [producer_id]
    
    if product_type:
        sql += " AND p.product_type = %s"
        params.append(product_type)
    
    if is_anti_gaspi is not None:
        sql += " AND p.is_anti_gaspi = %s"
        params.append(is_anti_gaspi)
    
    sql += " ORDER BY p.created_at DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)


def get_product_detail(product_id):
    """
    Get single product with full details including producer info.
    PostgreSQL: Fixed table names and column references.
    """
    sql = """
        SELECT 
            p.id, p.name, p.description, p.photo_url, p.sale_type,
            p.price, p.stock, p.product_type, p.harvest_date, 
            p.is_anti_gaspi, p.created_at, p.updated_at,
            pr.id as producer_id,
            pr.shop_name,
            pr.description as producer_description,
            pr.photo_url as producer_photo_url,
            pr.city,
            pr.wilaya,
            pr.is_bio_certified,
            u.id as user_id,
            u.email,
            u.phone as phone_number
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        INNER JOIN users u ON pr.user_id = u.id
        WHERE p.id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [product_id])
        return dict_fetchone(cursor)


def filter_products(sale_type=None, product_type=None, is_anti_gaspi=None, 
                   min_price=None, max_price=None, wilaya=None, limit=None):
    """
    Filter products by multiple criteria.
    PostgreSQL: Uses ILIKE for case-insensitive search on wilaya.
    """
    sql = """
        SELECT 
            p.id, p.name, p.photo_url, p.price, p.sale_type, p.stock,
            p.product_type, p.is_anti_gaspi, p.harvest_date,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE 1=1
    """
    params = []
    
    if sale_type:
        sql += " AND p.sale_type = %s"
        params.append(sale_type)
    
    if product_type:
        sql += " AND p.product_type = %s"
        params.append(product_type)
    
    if is_anti_gaspi is not None:
        sql += " AND p.is_anti_gaspi = %s"
        params.append(is_anti_gaspi)
    
    if min_price:
        sql += " AND p.price >= %s"
        params.append(min_price)
    
    if max_price:
        sql += " AND p.price <= %s"
        params.append(max_price)
    
    if wilaya:
        sql += " AND pr.wilaya ILIKE %s"
        params.append(f'%{wilaya}%')
    
    sql += " ORDER BY p.created_at DESC"
    
    if limit:
        sql += " LIMIT %s"
        params.append(limit)
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)


# ============================================
# PRODUCER QUERIES (Authenticated producer only)
# ============================================

def get_my_products(producer_id, product_type=None, is_anti_gaspi=None):
    """
    Get all products belonging to authenticated producer.
    """
    sql = """
        SELECT 
            p.id, p.name, p.photo_url, p.price, p.sale_type, p.stock,
            p.product_type, p.is_anti_gaspi, p.harvest_date, p.created_at,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE p.producer_id = %s
    """
    params = [producer_id]
    
    if product_type:
        sql += " AND p.product_type = %s"
        params.append(product_type)
    
    if is_anti_gaspi is not None:
        sql += " AND p.is_anti_gaspi = %s"
        params.append(is_anti_gaspi)
    
    sql += " ORDER BY p.created_at DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)


def get_my_product_detail(product_id, producer_id):
    """
    Get single product detail (only if owned by producer).
    """
    sql = """
        SELECT 
            p.id, p.name, p.description, p.photo_url, p.sale_type,
            p.price, p.stock, p.product_type, p.harvest_date,
            p.is_anti_gaspi, p.created_at, p.updated_at,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE p.id = %s AND p.producer_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [product_id, producer_id])
        return dict_fetchone(cursor)


def create_product(producer_id, name, description, photo_url, sale_type, 
                  price, stock, product_type, harvest_date, is_anti_gaspi):
    """
    Create a new product.
    PostgreSQL: Uses RETURNING clause to get created product data.
    """
    sql = """
        INSERT INTO products (
            producer_id, name, description, photo_url, sale_type,
            price, stock, product_type, harvest_date, is_anti_gaspi
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, producer_id, name, description, photo_url, sale_type,
                  price, stock, product_type, harvest_date, is_anti_gaspi,
                  created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [
            producer_id, name, description, photo_url, sale_type,
            price, stock, product_type, harvest_date, is_anti_gaspi
        ])
        return dict_fetchone(cursor)


def update_product(product_id, producer_id, name, description, photo_url, 
                  sale_type, price, stock, product_type, harvest_date, is_anti_gaspi):
    """
    Fully update a product (only if owned by producer).
    PostgreSQL: Uses RETURNING clause.
    """
    sql = """
        UPDATE products SET
            name = %s,
            description = %s,
            photo_url = %s,
            sale_type = %s,
            price = %s,
            stock = %s,
            product_type = %s,
            harvest_date = %s,
            is_anti_gaspi = %s
        WHERE id = %s AND producer_id = %s
        RETURNING id, producer_id, name, description, photo_url, sale_type,
                  price, stock, product_type, harvest_date, is_anti_gaspi,
                  created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [
            name, description, photo_url, sale_type, price, stock,
            product_type, harvest_date, is_anti_gaspi, product_id, producer_id
        ])
        return dict_fetchone(cursor)


def partial_update_product(product_id, producer_id, updates):
    """
    Partially update product with only provided fields.
    PostgreSQL: Dynamic UPDATE with RETURNING.
    """
    if not updates:
        return get_my_product_detail(product_id, producer_id)
    
    set_clauses = []
    params = []
    
    for field, value in updates.items():
        set_clauses.append(f"{field} = %s")
        params.append(value)
    
    params.extend([product_id, producer_id])
    
    sql = f"""
        UPDATE products SET
            {', '.join(set_clauses)}
        WHERE id = %s AND producer_id = %s
        RETURNING id, producer_id, name, description, photo_url, sale_type,
                  price, stock, product_type, harvest_date, is_anti_gaspi,
                  created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchone(cursor)


def delete_product(product_id, producer_id):
    """
    Delete product (only if owned by producer).
    PostgreSQL: Uses RETURNING to get deleted product name.
    """
    sql = """
        DELETE FROM products 
        WHERE id = %s AND producer_id = %s 
        RETURNING name
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [product_id, producer_id])
        result = cursor.fetchone()
        return result[0] if result else None


def toggle_anti_gaspi(product_id, producer_id):
    """
    Toggle anti-gaspi status for a product.
    PostgreSQL: Uses NOT to toggle boolean.
    """
    sql = """
        UPDATE products 
        SET is_anti_gaspi = NOT is_anti_gaspi
        WHERE id = %s AND producer_id = %s
        RETURNING id, name, is_anti_gaspi
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [product_id, producer_id])
        return dict_fetchone(cursor)


def get_producer_info(producer_id):
    """
    Get producer profile info (for product listing pages).
    """
    sql = """
        SELECT id, shop_name, description, photo_url,
               city, wilaya, is_bio_certified
        FROM producers
        WHERE id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [producer_id])
        return dict_fetchone(cursor)


# ============================================
# ANTI-GASPI AUTOMATION QUERIES
# ============================================

def get_anti_gaspi_eligible_products():
    """
    Get products eligible for anti-gaspi discount.
    
    UPDATED RULES: 
    - Perishable product types: Vegetables, Fruits, Dairy, Meat
    - >48h old (harvest_date set and >= 2 days ago)
    - Stock > 3
    - Not already anti-gaspi
    
    PostgreSQL: Uses CURRENT_DATE for date comparison.
    """
    sql = """
        SELECT 
            p.id, p.name, p.product_type, p.harvest_date, p.stock, p.price,
            pr.shop_name,
            CURRENT_DATE - p.harvest_date AS days_since_harvest
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE p.product_type IN ('Vegetables', 'Fruits', 'Dairy', 'Meat')
            AND p.harvest_date IS NOT NULL
            AND p.stock > 3
            AND CURRENT_DATE - p.harvest_date >= 2
            AND p.is_anti_gaspi = FALSE
        ORDER BY days_since_harvest DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return dict_fetchall(cursor)


def mark_products_as_anti_gaspi():
    """
    Automatically mark eligible products as anti-gaspi.
    
    UPDATED: Works with Vegetables, Fruits, Dairy, Meat
    
    Returns the number of products marked.
    PostgreSQL: Uses rowcount to get affected rows.
    """
    sql = """
        UPDATE products
        SET
            is_anti_gaspi = TRUE
            price = ROUND(price * 0.5, 2)
        WHERE product_type IN ('Vegetables', 'Fruits', 'Dairy', 'Meat')
            AND harvest_date IS NOT NULL
            AND stock > 3
            AND CURRENT_DATE - harvest_date >= 2
            AND is_anti_gaspi = FALSE
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.rowcount


def get_anti_gaspi_price(product_id):
    """
    Calculate 50% discount price for anti-gaspi product.
    PostgreSQL: Uses ROUND for decimal precision.
    """
    sql = """
        SELECT 
            id,
            name,
            price as original_price,
            ROUND(price * 0.5, 2) as anti_gaspi_price,
            is_anti_gaspi
        FROM products
        WHERE id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [product_id])
        return dict_fetchone(cursor)


def get_anti_gaspi_stats():
    """
    Get statistics about anti-gaspi products.
    Useful for admin dashboard.
    """
    sql = """
        SELECT 
            product_type,
            COUNT(*) as total_anti_gaspi,
            SUM(stock) as total_stock,
            AVG(CURRENT_DATE - harvest_date) as avg_days_old,
            SUM(price * stock) as original_value,
            SUM(ROUND(price * 0.5, 2) * stock) as discounted_value
        FROM products
        WHERE is_anti_gaspi = TRUE
        GROUP BY product_type
        ORDER BY total_anti_gaspi DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return dict_fetchall(cursor)
    # ============================================================
# ADD THIS FUNCTION TO YOUR queries.py
# Place it after the search_products function
# ============================================================

def search_products_advanced(search=None, producer_search=None, product_type=None, is_anti_gaspi=None, limit=20):
    """
    Advanced search for products by name AND/OR producer name.
    Supports filtering by product type and anti-gaspi status.
    """
    from django.db import connection
    
    sql = """
        SELECT 
            p.id, p.name, p.photo_url, p.price, p.sale_type, p.stock,
            p.product_type, p.is_anti_gaspi, p.harvest_date,
            pr.id as producer_id,
            pr.shop_name as producer_name
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE 1=1
    """
    params = []
    
    # Search product name or description
    if search:
        sql += " AND (p.name ILIKE %s OR p.description ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    # Search producer/shop name
    if producer_search:
        sql += " AND pr.shop_name ILIKE %s"
        params.append(f'%{producer_search}%')
    
    # Product type filter
    if product_type:
        sql += " AND p.product_type = %s"
        params.append(product_type)
    
    # Anti-gaspi filter
    if is_anti_gaspi is not None:
        sql += " AND p.is_anti_gaspi = %s"
        params.append(is_anti_gaspi)
    
    sql += " ORDER BY p.created_at DESC LIMIT %s"
    params.append(limit)
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ============================================
# SEASONAL BASKET QUERIES
# ============================================

def create_seasonal_basket(producer_id, name, description, discount_percentage, 
                          original_price, delivery_frequency='weekly', pickup_day='Saturday'):
    """Create a new seasonal basket."""
    discounted_price = float(original_price) * (1 - float(discount_percentage) / 100)
    
    sql = """
        INSERT INTO seasonal_baskets (
            producer_id, name, description, discount_percentage,
            original_price, discounted_price, delivery_frequency, pickup_day
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, producer_id, name, description, discount_percentage,
                  original_price, discounted_price, delivery_frequency, 
                  pickup_day, is_active, created_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [
            producer_id, name, description, discount_percentage,
            original_price, discounted_price, delivery_frequency, pickup_day
        ])
        return dict_fetchone(cursor)


def add_product_to_basket(basket_id, product_id, quantity):
    """Add a product to a seasonal basket."""
    sql = """
        INSERT INTO basket_products (basket_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (basket_id, product_id) 
        DO UPDATE SET quantity = %s
        RETURNING id, basket_id, product_id, quantity
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [basket_id, product_id, quantity, quantity])
        return dict_fetchone(cursor)


def remove_product_from_basket(basket_id, product_id):
    """Remove a product from a seasonal basket."""
    sql = "DELETE FROM basket_products WHERE basket_id = %s AND product_id = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [basket_id, product_id])
        return cursor.rowcount > 0


def get_basket_with_products(basket_id):
    """Get basket details with all products."""
    sql = """
        SELECT 
            sb.id, sb.producer_id, sb.name, sb.description, 
            sb.discount_percentage, sb.original_price, sb.discounted_price,
            sb.delivery_frequency, sb.is_active, sb.created_at,
            p.shop_name as producer_shop_name,
            p.photo_url as producer_banner,
            COUNT(DISTINCT cs.id) as subscriber_count
        FROM seasonal_baskets sb
        INNER JOIN producers p ON sb.producer_id = p.id
        LEFT JOIN client_subscriptions cs ON sb.id = cs.basket_id AND cs.status = 'active'
        WHERE sb.id = %s
        GROUP BY sb.id, p.shop_name, p.photo_url
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [basket_id])
        basket = dict_fetchone(cursor)
        
        if not basket:
            return None
        
        # Get products in basket - REMOVED is_active check
        products_sql = """
            SELECT 
                bp.quantity,
                p.id, p.name, p.description, p.photo_url, p.price,
                p.sale_type, p.product_type
            FROM basket_products bp
            INNER JOIN products p ON bp.product_id = p.id
            WHERE bp.basket_id = %s
        """
        cursor.execute(products_sql, [basket_id])
        basket['products'] = dict_fetchall(cursor)
        
        return basket
def get_producer_baskets(producer_id, is_active=None):
    """Get all baskets for a producer."""
    sql = """
        SELECT 
            sb.id, sb.name, sb.description, 
            sb.discount_percentage, sb.original_price, sb.discounted_price,
            sb.delivery_frequency, sb.is_active, sb.created_at,
            p.photo_url as producer_banner,
            COUNT(DISTINCT cs.id) as subscriber_count,
            COUNT(DISTINCT bp.product_id) as product_count
        FROM seasonal_baskets sb
        INNER JOIN producers p ON sb.producer_id = p.id
        LEFT JOIN client_subscriptions cs ON sb.id = cs.basket_id AND cs.status = 'active'
        LEFT JOIN basket_products bp ON sb.id = bp.basket_id
        WHERE sb.producer_id = %s
    """
    params = [producer_id]
    
    if is_active is not None:
        sql += " AND sb.is_active = %s"
        params.append(is_active)
    
    sql += " GROUP BY sb.id, p.photo_url ORDER BY sb.created_at DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)

def get_all_active_baskets(search=None, producer_id=None, limit=20):
    """Get all active seasonal baskets (for clients to browse)."""
    sql = """
        SELECT 
            sb.id, sb.name, sb.description,
            sb.discount_percentage, sb.original_price, sb.discounted_price,
            sb.delivery_frequency, sb.created_at,
            p.id as producer_id, p.shop_name, p.city, p.wilaya, p.is_bio_certified,
            COUNT(DISTINCT cs.id) as subscriber_count,
            COUNT(DISTINCT bp.product_id) as product_count
        FROM seasonal_baskets sb
        INNER JOIN producers p ON sb.producer_id = p.id
        LEFT JOIN client_subscriptions cs ON sb.id = cs.basket_id AND cs.status = 'active'
        LEFT JOIN basket_products bp ON sb.id = bp.basket_id
        WHERE sb.is_active = TRUE
    """
    params = []
    
    if search:
        sql += " AND (sb.name ILIKE %s OR sb.description ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if producer_id:
        sql += " AND sb.producer_id = %s"
        params.append(producer_id)
    
    sql += " GROUP BY sb.id, p.id ORDER BY sb.created_at DESC LIMIT %s"
    params.append(limit)
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)



def update_basket(basket_id, producer_id, **updates):
    """Update basket details."""
    # Recalculate discounted price if needed
    if 'discount_percentage' in updates or 'original_price' in updates:
        current = get_basket_with_products(basket_id)
        discount = updates.get('discount_percentage', current['discount_percentage'])
        original = updates.get('original_price', current['original_price'])
        updates['discounted_price'] = original * (1 - discount / 100)
    
    set_clauses = []
    params = []
    
    for field, value in updates.items():
        set_clauses.append(f"{field} = %s")
        params.append(value)
    
    if not set_clauses:
        return get_basket_with_products(basket_id)
    
    params.extend([basket_id, producer_id])
    
    sql = f"""
        UPDATE seasonal_baskets SET
            {', '.join(set_clauses)}, updated_at = NOW()
        WHERE id = %s AND producer_id = %s
        RETURNING id
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        if cursor.rowcount == 0:
            return None
        return get_basket_with_products(basket_id)


def delete_basket(basket_id, producer_id):
    """Delete a seasonal basket."""
    sql = "DELETE FROM seasonal_baskets WHERE id = %s AND producer_id = %s RETURNING name"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [basket_id, producer_id])
        result = cursor.fetchone()
        return result[0] if result else None


# ============================================
# SUBSCRIPTION QUERIES
# ============================================

def create_subscription(client_id, basket_id, delivery_method, delivery_address=None, pickup_point_id=None):
    """Create a new subscription."""
    from datetime import date, timedelta
    
    next_delivery = date.today() + timedelta(days=7)  # First delivery in 7 days
    
    sql = """
        INSERT INTO client_subscriptions (
            client_id, basket_id, delivery_method, delivery_address,
            pickup_point_id, next_delivery_date
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, client_id, basket_id, status, start_date, next_delivery_date,
                  delivery_method, delivery_address, pickup_point_id, created_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [
            client_id, basket_id, delivery_method, delivery_address,
            pickup_point_id, next_delivery
        ])
        return dict_fetchone(cursor)


def get_client_subscriptions(client_id, status=None):   
    """Get all subscriptions for a client with basket details."""
    sql = """
        SELECT 
            cs.id,
            cs.client_id,
            cs.basket_id,
            cs.status,
            cs.start_date,
            cs.next_delivery_date,
            cs.delivery_method,
            cs.delivery_address,
            cs.pickup_point_id,
            cs.total_deliveries,
            sb.name as basket_name,
            sb.description as basket_description,
            sb.original_price,
            sb.discounted_price,
            sb.discount_percentage,
            sb.delivery_frequency,
            sb.pickup_day,
            p.id as producer_id,
            p.shop_name,
            p.city,
            p.wilaya,
            p.photo_url as producer_banner,
            COUNT(bp.id) as product_count
        FROM client_subscriptions cs
        INNER JOIN seasonal_baskets sb ON cs.basket_id = sb.id
        INNER JOIN producers p ON sb.producer_id = p.id
        LEFT JOIN basket_products bp ON sb.id = bp.basket_id
        WHERE cs.client_id = %s
    """
    
    params = [client_id]
    
    # ✅ Add status filter if provided
    if status:
        sql += " AND cs.status = %s"
        params.append(status)
    
    sql += """
        GROUP BY 
            cs.id, cs.client_id, cs.basket_id, cs.status, 
            cs.start_date, cs.next_delivery_date, cs.delivery_method,
            cs.delivery_address, cs.pickup_point_id, cs.total_deliveries,
            sb.name, sb.description, sb.original_price, sb.discounted_price,
            sb.discount_percentage, sb.delivery_frequency, sb.pickup_day,
            p.id, p.shop_name, p.city, p.wilaya, p.photo_url
        ORDER BY cs.created_at DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)

def get_basket_subscribers(basket_id, producer_id):
    """Get all subscribers for a basket (producer view)."""
    sql = """
        SELECT 
            cs.id as subscription_id, cs.status, cs.start_date, cs.next_delivery_date,
            cs.total_deliveries, cs.delivery_method,
            c.id as client_id,
            u.first_name, u.last_name, u.email, u.phone
        FROM client_subscriptions cs
        INNER JOIN clients c ON cs.client_id = c.id
        INNER JOIN users u ON c.user_id = u.id
        INNER JOIN seasonal_baskets sb ON cs.basket_id = sb.id
        WHERE cs.basket_id = %s AND sb.producer_id = %s
        ORDER BY cs.created_at DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [basket_id, producer_id])
        return dict_fetchall(cursor)


def update_subscription_status(subscription_id, client_id, status):
    """Update subscription status (pause/cancel/reactivate)."""
    from datetime import datetime
    
    extra_set = ""
    params = [status]
    
    if status == 'cancelled':
        extra_set = ", cancelled_at = %s"
        params.append(datetime.now())
    
    params.extend([subscription_id, client_id])
    
    sql = f"""
        UPDATE client_subscriptions SET
            status = %s{extra_set}, updated_at = NOW()
        WHERE id = %s AND client_id = %s
        RETURNING id, status
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchone(cursor)


def process_weekly_deliveries():
    """
    Create delivery records for subscriptions due.
    Run this as a scheduled task (cron job).
    """
    from datetime import date
    
    sql = """
        INSERT INTO subscription_deliveries (subscription_id, delivery_date)
        SELECT id, next_delivery_date
        FROM client_subscriptions
        WHERE status = 'active'
          AND next_delivery_date <= %s
          AND NOT EXISTS (
              SELECT 1 FROM subscription_deliveries sd
              WHERE sd.subscription_id = client_subscriptions.id
                AND sd.delivery_date = client_subscriptions.next_delivery_date
          )
        RETURNING subscription_id
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [date.today()])
        created = cursor.fetchall()
        
        # Update next delivery dates
        if created:
            update_sql = """
                UPDATE client_subscriptions
                SET next_delivery_date = next_delivery_date + INTERVAL '7 days',
                    total_deliveries = total_deliveries + 1
                WHERE id = ANY(%s)
            """
            cursor.execute(update_sql, [[row[0] for row in created]])
        
        return len(created)
