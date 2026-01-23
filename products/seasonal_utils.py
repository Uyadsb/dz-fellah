"""
Seasonal product utilities for DZ-Fellah
Checks if products are currently in season based on their names
"""
from datetime import datetime
from django.db import connection


def normalize_text(text):
    """
    Normalize text for fuzzy matching.
    Handles case, accents, and extra spaces.
    """
    if not text:
        return ''
    
    # Convert to lowercase and remove extra spaces
    normalized = text.lower().strip()
    
    # Remove accents for better matching
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e',
        'à': 'a', 'â': 'a',
        'ô': 'o',
        'û': 'u', 'ù': 'u',
        'ï': 'i', 'î': 'i',
        'ç': 'c'
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized


def is_product_in_season(product_name, current_month=None):
    """
    Check if a product is currently in season using fuzzy name matching.
    
    Examples:
        - "Cherry Tomatoes" matches "Tomato" → checks tomato season
        - "Red Onion" matches "Onion" → checks onion season
        - "Fresh Strawberries" matches "Strawberry" → checks strawberry season
    
    Args:
        product_name: Name of the product to check
        current_month: Month number (1-12), defaults to current month
    
    Returns:
        bool: True if product is in season, False otherwise
    """
    if not product_name:
        return False
    
    if current_month is None:
        current_month = datetime.now().month
    
    # Normalize product name for matching
    product_normalized = normalize_text(product_name)
    
    cursor = connection.cursor()
    
    # Get all seasonal products from database
    cursor.execute("""
        SELECT product_name, start_month, end_month 
        FROM product_seasons
    """)
    
    rows = cursor.fetchall()
    cursor.close()
    
    # Check fuzzy matches
    for seasonal_name, start_month, end_month in rows:
        seasonal_normalized = normalize_text(seasonal_name)
        
        # Fuzzy match: check if seasonal name is contained in product name
        # Examples: 
        #   - "tomato" in "cherry tomatoes" → MATCH
        #   - "strawberry" in "fresh strawberries" → MATCH
        #   - "onion" in "red onion" → MATCH
        if seasonal_normalized in product_normalized or product_normalized in seasonal_normalized:
            # Check if current month is in season range
            if start_month <= end_month:
                # Normal season (e.g., May-September: 5-9)
                if start_month <= current_month <= end_month:
                    return True
            else:
                # Cross-year season (e.g., November-April: 11-4)
                # Handles seasons that span year boundary
                if current_month >= start_month or current_month <= end_month:
                    return True
    
    return False