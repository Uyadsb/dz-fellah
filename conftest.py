"""
Pytest configuration and shared fixtures.
"""
import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Configure test database.
    Uses the same database as development but with transaction rollback.
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings.DATABASES['default']['NAME'],
        'USER': settings.DATABASES['default']['USER'],
        'PASSWORD': settings.DATABASES['default']['PASSWORD'],
        'HOST': settings.DATABASES['default']['HOST'],
        'PORT': settings.DATABASES['default']['PORT'],
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'client_encoding': 'UTF8',
        }
    }


@pytest.fixture(scope='function')
def clean_db(django_db_setup, django_db_blocker):
    """
    Clean database before each test.
    Deletes all data but keeps schema.
    """
    from django.db import connection
    
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            # Disable foreign key checks temporarily
            cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
            
            # Truncate all tables
            cursor.execute("""
                TRUNCATE TABLE products, producers, clients, users RESTART IDENTITY CASCADE;
            """)
            
            # Re-enable foreign key checks
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE;")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings."""
    # Suppress warnings if needed
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)