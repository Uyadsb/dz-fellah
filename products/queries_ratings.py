from django.db import connection


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Return one row from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# ================================
# CHECK QUERIES
# ================================

def check_user_purchased_product(user_id, product_id):
    """
    Check if user has purchased this product
    
    Returns: bool
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 
                FROM sub_orders so
                INNER JOIN order_items oi ON so.id = oi.sub_order_id
                INNER JOIN orders o ON so.parent_order_id = o.id
                WHERE o.client_id = %s 
                AND oi.product_id = %s
                AND so.status IN ('completed', 'ready', 'preparing', 'confirmed')
            ) AS has_purchased
        """, [user_id, product_id])
        
        result = cursor.fetchone()
        return result[0] if result else False


def check_user_owns_product(user_id, product_id):
    """
    Check if user is the producer of this product
    
    Returns: bool
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 
                FROM products 
                WHERE id = %s AND producer_id = %s
            ) AS owns_product
        """, [product_id, user_id])
        
        result = cursor.fetchone()
        return result[0] if result else False


def get_user_type(user_id):
    """
    Get user type
    
    Returns: str ('client' or 'producer') or None
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_type FROM users WHERE id = %s
        """, [user_id])
        
        result = cursor.fetchone()
        return result[0] if result else None


def get_product_basic_info(product_id):
    """
    Get basic product information
    
    Returns: dict with id, name, producer_id or None
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, producer_id 
            FROM products 
            WHERE id = %s
        """, [product_id])
        
        return dictfetchone(cursor)


# ================================
# RATING CRUD QUERIES
# ================================

def insert_or_update_rating(product_id, user_id, rating, created_at, updated_at):
    """
    Insert or update a product rating
    
    Returns: dict with rating data
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_ratings (product_id, user_id, rating, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id, user_id) 
            DO UPDATE SET 
                rating = EXCLUDED.rating,
                updated_at = EXCLUDED.updated_at
            RETURNING id, product_id, user_id, rating, created_at, updated_at
        """, [product_id, user_id, rating, created_at, updated_at])
        
        return dictfetchone(cursor)


def get_user_rating_for_product(user_id, product_id):
    """
    Get user's rating for a specific product
    
    Returns: dict with rating, created_at, updated_at or None
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT rating, created_at, updated_at 
            FROM product_ratings 
            WHERE product_id = %s AND user_id = %s
        """, [product_id, user_id])
        
        return dictfetchone(cursor)


def delete_user_rating(user_id, product_id):
    """
    Delete user's rating for a product
    
    Returns: bool (True if deleted, False if not found)
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM product_ratings 
            WHERE product_id = %s AND user_id = %s
            RETURNING id
        """, [product_id, user_id])
        
        deleted = cursor.fetchone()
        return deleted is not None


# ================================
# RATING SUMMARY QUERIES
# ================================

def get_product_rating_summary(product_id):
    """
    Get rating summary for a product
    
    Returns: dict with product_id, product_name, producer_id, total_ratings, 
             average_rating, star_distribution
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM product_rating_summary WHERE product_id = %s
        """, [product_id])
        
        return dictfetchone(cursor)


def get_producer_rating_summary(producer_id):
    """
    Get rating summary for a producer (based on all their products)
    
    Returns: dict with producer_id, producer_name, total_products, 
             total_ratings, average_rating
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM producer_rating_summary WHERE producer_id = %s
        """, [producer_id])
        
        return dictfetchone(cursor)