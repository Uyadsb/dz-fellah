"""
Database connection utilities for DZ-Fellah.
Provides both Django's connection and raw psycopg2 connections.
"""

from django.conf import settings
from django.db import connection as django_connection


def get_connection():
    """
    Get Django's database connection.
    
    This is the recommended way to get a database connection
    since it's already configured in settings.py and managed
    by Django's connection pooling.
    
    Returns:
        django.db.backends.postgresql.base.DatabaseWrapper
    
    Example:
        from db.connection import get_connection
        
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
            result = cursor.fetchone()
    """
    return django_connection


def get_cursor():
    """
    Get a database cursor from Django's connection.
    
    This is a convenience method for getting a cursor directly.
    Remember to use it in a context manager (with statement).
    
    Returns:
        Database cursor
    
    Example:
        from db.connection import get_cursor
        
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
    """
    return django_connection.cursor()


def test_connection():
    """
    Test database connection.
    
    Returns:
        dict: Connection status and database info
    
    Example:
        from db.connection import test_connection
        
        result = test_connection()
        print(result)
        # {'success': True, 'database': 'dzfellah', 'user': 'postgres', ...}
    """
    try:
        with django_connection.cursor() as cursor:
            # Get PostgreSQL version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Get current database name
            cursor.execute("SELECT current_database();")
            database = cursor.fetchone()[0]
            
            # Get current user
            cursor.execute("SELECT current_user;")
            user = cursor.fetchone()[0]
            
            # Count tables
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            return {
                'success': True,
                'database': database,
                'user': user,
                'table_count': table_count,
                'version': version.split(',')[0],
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }




def execute_sql_file(file_path):
    """
    Execute SQL commands from a file.
    
    Useful for running schema files.
    
    Args:
        file_path (str): Path to SQL file
    
    Returns:
        dict: Execution status
    
    Example:
        from db.connection import execute_sql_file
        
        result = execute_sql_file('db/schemas/01_users_schema.sql')
        print(result)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        with django_connection.cursor() as cursor:
            cursor.execute(sql)
        
        return {
            'success': True,
            'file': file_path,
            'message': 'SQL file executed successfully'
        }
    except Exception as e:
        return {
            'success': False,
            'file': file_path,
            'error': str(e)
        }


def dict_fetchall(cursor):
    """
    Convert cursor results to list of dictionaries.
    
    Args:
        cursor: Database cursor
    
    Returns:
        list: List of dictionaries with column names as keys
    
    Example:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = dict_fetchall(cursor)
            # [{'id': 1, 'email': 'test@test.com', ...}, ...]
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    """
    Convert single cursor result to dictionary.
    
    Args:
        cursor: Database cursor
    
    Returns:
        dict or None: Dictionary with column names as keys, or None if no result
    
    Example:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", [1])
            user = dict_fetchone(cursor)
            # {'id': 1, 'email': 'test@test.com', ...}
    """
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None