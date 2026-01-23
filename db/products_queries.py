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
    Rules: fresh products, >48h old, stock > 3, not already anti-gaspi.
    PostgreSQL: Uses CURRENT_DATE for date comparison.
    """
    sql = """
        SELECT 
            p.id, p.name, p.harvest_date, p.stock, p.price,
            pr.shop_name,
            CURRENT_DATE - p.harvest_date AS days_since_harvest
        FROM products p
        INNER JOIN producers pr ON p.producer_id = pr.id
        WHERE p.product_type = 'fresh'
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
    Returns the number of products marked.
    PostgreSQL: Uses rowcount to get affected rows.
    """
    sql = """
        UPDATE products
        SET is_anti_gaspi = TRUE
        WHERE product_type = 'fresh'
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