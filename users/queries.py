from django.db import connection
from django.contrib.auth.hashers import make_password, check_password


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
# USER QUERIES
# ============================================

def get_user_by_email(email):
<<<<<<< HEAD
    """Get user by email with profile data - SINGLE QUERY."""
=======
    """
    Get user by email with profile data - SINGLE QUERY.
    PostgreSQL: Uses LEFT JOIN for optional relationships.
    """
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    sql = """
        SELECT 
            u.id, u.email, u.user_type, u.first_name, u.last_name,
            u.phone, u.is_active, u.is_verified, u.created_at, u.updated_at,
            u.password,
            p.id as producer_id, p.shop_name, p.description as producer_description,
<<<<<<< HEAD
            p.photo_url as producer_photo, 
            p.avatar as producer_avatar,
            p.address as producer_address,
            p.city as producer_city, p.wilaya as producer_wilaya,
            p.methods, p.is_bio_certified, p.created_at as producer_created_at,
            c.id as client_id, 
            c.avatar as client_avatar,
            c.address as client_address,
=======
            p.photo_url as producer_photo, p.address as producer_address,
            p.city as producer_city, p.wilaya as producer_wilaya,
            p.methods, p.is_bio_certified, p.created_at as producer_created_at,
            c.id as client_id, c.address as client_address,
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            c.city as client_city, c.wilaya as client_wilaya,
            c.created_at as client_created_at
        FROM users u
        LEFT JOIN producers p ON u.id = p.user_id
        LEFT JOIN clients c ON u.id = c.user_id
        WHERE u.email = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [email])
        return dict_fetchone(cursor)


def get_user_by_id(user_id):
<<<<<<< HEAD
    """Get user by ID with profile data - SINGLE QUERY."""
=======
    """
    Get user by ID with profile data - SINGLE QUERY.
    PostgreSQL: Uses LEFT JOIN for optional relationships.
    """
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    sql = """
        SELECT 
            u.id, u.email, u.user_type, u.first_name, u.last_name,
            u.phone, u.is_active, u.is_verified, u.created_at, u.updated_at,
            p.id as producer_id, p.shop_name, p.description as producer_description,
<<<<<<< HEAD
            p.photo_url as producer_photo,
            p.avatar as producer_avatar,
            p.address as producer_address,
            p.city as producer_city, p.wilaya as producer_wilaya,
            p.methods, p.is_bio_certified, p.created_at as producer_created_at,
            c.id as client_id,
            c.avatar as client_avatar,
            c.address as client_address,
=======
            p.photo_url as producer_photo, p.address as producer_address,
            p.city as producer_city, p.wilaya as producer_wilaya,
            p.methods, p.is_bio_certified, p.created_at as producer_created_at,
            c.id as client_id, c.address as client_address,
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            c.city as client_city, c.wilaya as client_wilaya,
            c.created_at as client_created_at
        FROM users u
        LEFT JOIN producers p ON u.id = p.user_id
        LEFT JOIN clients c ON u.id = c.user_id
        WHERE u.id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        return dict_fetchone(cursor)

<<<<<<< HEAD
=======

>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
def email_exists(email):
    """
    Check if email already exists.
    PostgreSQL: Uses EXISTS for efficient checking.
    """
    sql = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s)"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [email])
        return cursor.fetchone()[0]


def create_user(email, password, user_type, first_name, last_name, phone=None):
    """
    Create a new user.
    PostgreSQL: Uses RETURNING clause to get created user data.
    """
    hashed_password = make_password(password)
    
    sql = """
        INSERT INTO users (email, password, user_type, first_name, last_name, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, email, user_type, first_name, last_name, phone, 
                  is_active, is_verified, created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [
            email, hashed_password, user_type, first_name, last_name, phone
        ])
        return dict_fetchone(cursor)


def verify_password(stored_password, raw_password):
    """
    Verify password against stored hash.
    Uses Django's check_password for bcrypt/PBKDF2 verification.
    """
    return check_password(raw_password, stored_password)


def update_user_password(user_id, new_password):
    """
    Update user password.
    PostgreSQL: Hashes password before storing.
    """
    hashed_password = make_password(new_password)
    
    sql = "UPDATE users SET password = %s WHERE id = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [hashed_password, user_id])


# ============================================
# PRODUCER QUERIES
# ============================================

def create_producer_profile(user_id, shop_name, description=None, photo_url=None,
                           address=None, city=None, wilaya=None, methods=None,
                           is_bio_certified=False):
    """
    Create producer profile.
    PostgreSQL: Uses RETURNING clause.
    """
    sql = """
        INSERT INTO producers (
            user_id, shop_name, description, photo_url, address,
            city, wilaya, methods, is_bio_certified
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, shop_name, description, photo_url, address,
                  city, wilaya, methods, is_bio_certified, created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [
            user_id, shop_name, description, photo_url, address,
            city, wilaya, methods, is_bio_certified
        ])
        return dict_fetchone(cursor)


def get_producer_profile(user_id):
    """
    Get producer profile by user_id.
    """
    sql = """
        SELECT id, user_id, shop_name, description, photo_url, address,
               city, wilaya, methods, is_bio_certified, created_at, updated_at
        FROM producers
        WHERE user_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        return dict_fetchone(cursor)


def get_producer_profile_by_id(producer_id):
    """
    Get producer profile by producer ID.
    """
    sql = """
        SELECT id, user_id, shop_name, description, photo_url, address,
               city, wilaya, methods, is_bio_certified, created_at, updated_at
        FROM producers
        WHERE id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [producer_id])
        return dict_fetchone(cursor)


<<<<<<< HEAD

=======
def update_producer_profile(user_id, updates):
    """
    Update producer profile with provided fields.
    PostgreSQL: Dynamic UPDATE with RETURNING.
    """
    if not updates:
        return get_producer_profile(user_id)
    
    set_clauses = []
    params = []
    
    for field, value in updates.items():
        set_clauses.append(f"{field} = %s")
        params.append(value)
    
    params.append(user_id)
    
    sql = f"""
        UPDATE producers SET
            {', '.join(set_clauses)}
        WHERE user_id = %s
        RETURNING id, user_id, shop_name, description, photo_url, address,
                  city, wilaya, methods, is_bio_certified, created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchone(cursor)
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b


# ============================================
# CLIENT QUERIES
# ============================================

def create_client_profile(user_id, address=None, city=None, wilaya=None):
    """
    Create client profile.
    PostgreSQL: Uses RETURNING clause.
    """
    sql = """
        INSERT INTO clients (user_id, address, city, wilaya)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, address, city, wilaya, created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id, address, city, wilaya])
        return dict_fetchone(cursor)


def get_client_profile(user_id):
    """
    Get client profile by user_id.
    """
    sql = """
        SELECT id, user_id, address, city, wilaya, created_at, updated_at
        FROM clients
        WHERE user_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        return dict_fetchone(cursor)


<<<<<<< HEAD
=======
def update_client_profile(user_id, updates):
    """
    Update client profile with provided fields.
    PostgreSQL: Dynamic UPDATE with RETURNING.
    """
    if not updates:
        return get_client_profile(user_id)
    
    set_clauses = []
    params = []
    
    for field, value in updates.items():
        set_clauses.append(f"{field} = %s")
        params.append(value)
    
    params.append(user_id)
    
    sql = f"""
        UPDATE clients SET
            {', '.join(set_clauses)}
        WHERE user_id = %s
        RETURNING id, user_id, address, city, wilaya, created_at, updated_at
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchone(cursor)
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b


# ============================================
# LIST QUERIES
# ============================================

<<<<<<< HEAD
def get_all_producers(city=None, wilaya=None, is_bio_certified=None, search=None):  # ✅ ADD search
=======
def get_all_producers(city=None, wilaya=None, is_bio_certified=None):
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    """
    Get all producers with optional filters - SINGLE QUERY.
    PostgreSQL: Uses ILIKE for case-insensitive search.
    """
    sql = """
        SELECT 
            p.id, p.shop_name, p.description, p.photo_url,
            p.address, p.city, p.wilaya, p.methods, p.is_bio_certified,
            p.created_at,
            u.id as user_id, u.email, u.first_name, u.last_name, u.phone
        FROM producers p
        INNER JOIN users u ON p.user_id = u.id
        WHERE u.is_active = TRUE
    """
    params = []
    
<<<<<<< HEAD
    # ✅ ADD THIS
    if search:
        sql += " AND p.shop_name ILIKE %s"
        params.append(f'%{search}%')
    
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
    if city:
        sql += " AND p.city ILIKE %s"
        params.append(f'%{city}%')
    
    if wilaya:
        sql += " AND p.wilaya ILIKE %s"
        params.append(f'%{wilaya}%')
    
    if is_bio_certified is not None:
        sql += " AND p.is_bio_certified = %s"
        params.append(is_bio_certified)
    
    sql += " ORDER BY p.created_at DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)

<<<<<<< HEAD
=======

>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
def get_all_clients(city=None, wilaya=None):
    """
    Get all clients with optional filters - SINGLE QUERY.
    PostgreSQL: Uses ILIKE for case-insensitive search.
    """
    sql = """
        SELECT 
            c.id, c.address, c.city, c.wilaya, c.created_at,
            u.id as user_id, u.email, u.first_name, u.last_name, u.phone
        FROM clients c
        INNER JOIN users u ON c.user_id = u.id
        WHERE u.is_active = TRUE
    """
    params = []
    
    if city:
        sql += " AND c.city ILIKE %s"
        params.append(f'%{city}%')
    
    if wilaya:
        sql += " AND c.wilaya ILIKE %s"
        params.append(f'%{wilaya}%')
    
    sql += " ORDER BY c.created_at DESC"
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return dict_fetchall(cursor)


# ============================================
# HELPER FUNCTION FOR STRUCTURING USER DATA
# ============================================

def structure_user_data(user_row):
    """
    Structure user data from raw SQL result.
    Separates user fields from profile fields.
    
    Args:
        user_row (dict): Raw SQL result with joined user and profile data
    
    Returns:
        dict: Structured user data with nested profile objects
    """
    if not user_row:
        return None
    
    user_data = {
        'id': user_row['id'],
        'email': user_row['email'],
        'user_type': user_row['user_type'],
        'first_name': user_row['first_name'],
        'last_name': user_row['last_name'],
        'phone': user_row.get('phone'),
        'is_active': user_row['is_active'],
        'is_verified': user_row['is_verified'],
        'created_at': user_row['created_at'],
        'updated_at': user_row['updated_at'],
    }
    
    # Add producer profile if exists
    if user_row.get('producer_id'):
        user_data['producer_profile'] = {
            'id': user_row['producer_id'],
            'shop_name': user_row['shop_name'],
            'description': user_row.get('producer_description'),
            'photo_url': user_row.get('producer_photo'),
            'address': user_row.get('producer_address'),
<<<<<<< HEAD
            'avatar': user_row.get('producer_avatar'),
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            'city': user_row.get('producer_city'),
            'wilaya': user_row.get('producer_wilaya'),
            'methods': user_row.get('methods'),
            'is_bio_certified': user_row.get('is_bio_certified', False),
            'created_at': user_row.get('producer_created_at'),
        }
    else:
        user_data['producer_profile'] = None
    
    # Add client profile if exists
    if user_row.get('client_id'):
        user_data['client_profile'] = {
            'id': user_row['client_id'],
<<<<<<< HEAD
            'avatar': user_row.get('client_avatar'), 
=======
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
            'address': user_row.get('client_address'),
            'city': user_row.get('client_city'),
            'wilaya': user_row.get('client_wilaya'),
            'created_at': user_row.get('client_created_at'),
        }
    else:
        user_data['client_profile'] = None
    
<<<<<<< HEAD
    return user_data
# Add these functions to users/queries.py

def update_user(user_id, **kwargs):
    """Update user fields."""
    from django.db import connection
    
    # Build SET clause dynamically
    set_clauses = []
    params = []
    
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    if not set_clauses:
        return
    
    params.append(user_id)
    
    sql = f"""
        UPDATE users
        SET {', '.join(set_clauses)}, updated_at = NOW()
        WHERE id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)


def update_client_profile(user_id, **kwargs):
    """Update client profile fields."""
    from django.db import connection
    
    set_clauses = []
    params = []
    
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    if not set_clauses:
        return
    
    params.append(user_id)
    
    sql = f"""
        UPDATE clients
        SET {', '.join(set_clauses)}, updated_at = NOW()
        WHERE user_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)


def update_producer_profile(user_id, **kwargs):
    """Update producer profile fields."""
    from django.db import connection
    
    set_clauses = []
    params = []
    
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    
    if not set_clauses:
        return
    
    params.append(user_id)
    
    sql = f"""
        UPDATE producers
        SET {', '.join(set_clauses)}, updated_at = NOW()
        WHERE user_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
=======
    return user_data
>>>>>>> 33f7a2d22d51c7734ecadb4759a1c8c2dc77ec6b
