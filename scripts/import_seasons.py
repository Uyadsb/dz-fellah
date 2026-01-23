"""
Seasonal Data Import Script for DZ-Fellah
Cleans and imports seasonal data from CSV into PostgreSQL database
Handles typos, plurals, Arabic/French/English variations, and dirty data
"""

import csv
import os
import sys
from pathlib import Path

# Add parent directory to path to import Django settings
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection


def normalize_for_matching(text):
    """
    Advanced text normalization for fuzzy matching.
    Handles typos, plurals, Arabic/French/English variations.
    """
    if not text:
        return ''
    
    text = text.lower().strip()
    
    # Remove accents
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e',
        'à': 'a', 'â': 'a',
        'ô': 'o', 'ö': 'o',
        'û': 'u', 'ù': 'u', 'ü': 'u',
        'ï': 'i', 'î': 'i',
        'ç': 'c'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove plurals (basic)
    if text.endswith('es'):
        text = text[:-2]
    elif text.endswith('s'):
        text = text[:-1]
    
    return text


def find_canonical_name(input_name):
    """
    Find the canonical (standard) product name from variations.
    Handles typos, plurals, Arabic/French/English.
    """
    
    # Dictionary of variations → canonical name
    name_variations = {
        # Tomatoes - طماطم
        'tomato': 'Tomato',
        'tomate': 'Tomato',
        'tomatos': 'Tomato',
        'tomates': 'Tomato',
        'tomatoe': 'Tomato',
        'طماطم': 'Tomato',
        'طماطة': 'Tomato',
        'بندورة': 'Tomato',
        
        # Potatoes - بطاطا
        'potato': 'Potato',
        'potatoes': 'Potato',
        'pomme de terre': 'Potato',
        'patato': 'Potato',
        'potatoe': 'Potato',
        'بطاطا': 'Potato',
        'بطاطس': 'Potato',
        
        # Zucchini - كوسة
        'zucchini': 'Zucchini',
        'courgette': 'Zucchini',
        'zuchini': 'Zucchini',
        'zuccini': 'Zucchini',
        'كوسة': 'Zucchini',
        'كوسا': 'Zucchini',
        
        # Eggplant - باذنجان
        'eggplant': 'Eggplant',
        'aubergine': 'Eggplant',
        'egplant': 'Eggplant',
        'باذنجان': 'Eggplant',
        'بادنجان': 'Eggplant',
        
        # Pepper - فلفل
        'pepper': 'Pepper',
        'poivron': 'Pepper',
        'peper': 'Pepper',
        'pepr': 'Pepper',
        'فلفل': 'Pepper',
        'فليفلة': 'Pepper',
        
        # Cucumber - خيار
        'cucumber': 'Cucumber',
        'concombre': 'Cucumber',
        'cucmber': 'Cucumber',
        'خيار': 'Cucumber',
        
        # Carrot - جزر
        'carrot': 'Carrot',
        'carrots': 'Carrot',
        'carot': 'Carrot',
        'carotte': 'Carrot',
        'جزر': 'Carrot',
        
        # Onion - بصل
        'onion': 'Onion',
        'oignon': 'Onion',
        'onon': 'Onion',
        'بصل': 'Onion',
        'بصلة': 'Onion',
        
        # Garlic - ثوم
        'garlic': 'Garlic',
        'ail': 'Garlic',
        'garlik': 'Garlic',
        'ثوم': 'Garlic',
        
        # Bean - فاصوليا
        'bean': 'Bean',
        'haricot': 'Bean',
        'been': 'Bean',
        'فاصوليا': 'Bean',
        'لوبيا': 'Bean',
        
        # Pea - بازلاء
        'pea': 'Pea',
        'peas': 'Pea',
        'petit pois': 'Pea',
        'petits pois': 'Pea',
        'بازلاء': 'Pea',
        'جلبانة': 'Pea',
        
        # Fava - فول
        'fava': 'Fava',
        'feve': 'Fava',
        'fève': 'Fava',
        'فول': 'Fava',
        
        # Artichoke - خرشوف
        'artichoke': 'Artichoke',
        'artichaut': 'Artichoke',
        'artichok': 'Artichoke',
        'خرشوف': 'Artichoke',
        'قرنون': 'Artichoke',
        
        # Cabbage - ملفوف
        'cabbage': 'Cabbage',
        'chou': 'Cabbage',
        'cabagge': 'Cabbage',
        'ملفوف': 'Cabbage',
        'كرنب': 'Cabbage',
        
        # Turnip - لفت
        'turnip': 'Turnip',
        'navet': 'Turnip',
        'turnep': 'Turnip',
        'لفت': 'Turnip',
        
        # Beet - شمندر
        'beet': 'Beet',
        'beetroot': 'Beet',
        'betterave': 'Beet',
        'شمندر': 'Beet',
        'بنجر': 'Beet',
        
        # Lettuce - خس
        'lettuce': 'Lettuce',
        'laitue': 'Lettuce',
        'letuce': 'Lettuce',
        'خس': 'Lettuce',
        
        # Spinach - سبانخ
        'spinach': 'Spinach',
        'epinard': 'Spinach',
        'spinch': 'Spinach',
        'سبانخ': 'Spinach',
        
        # Orange - برتقال
        'orange': 'Orange',
        'oranje': 'Orange',
        'برتقال': 'Orange',
        'برتقالة': 'Orange',
        
        # Lemon - ليمون
        'lemon': 'Lemon',
        'citron': 'Lemon',
        'limon': 'Lemon',
        'ليمون': 'Lemon',
        'ليمونة': 'Lemon',
        'حامض': 'Lemon',
        
        # Mandarin - يوسفي
        'mandarin': 'Mandarin',
        'mandarine': 'Mandarin',
        'manderine': 'Mandarin',
        'يوسفي': 'Mandarin',
        'مندرين': 'Mandarin',
        
        # Strawberry - فراولة
        'strawberry': 'Strawberry',
        'strawberries': 'Strawberry',
        'fraise': 'Strawberry',
        'strwberry': 'Strawberry',
        'strawbery': 'Strawberry',
        'فراولة': 'Strawberry',
        'فريز': 'Strawberry',
        'توت الأرض': 'Strawberry',
        
        # Melon - شمام
        'melon': 'Melon',
        'mellon': 'Melon',
        'شمام': 'Melon',
        'بطيخ أصفر': 'Melon',
        
        # Watermelon - دلاح
        'watermelon': 'Watermelon',
        'pasteque': 'Watermelon',
        'pastèque': 'Watermelon',
        'water melon': 'Watermelon',
        'دلاح': 'Watermelon',
        'بطيخ': 'Watermelon',
        'حبحب': 'Watermelon',
        
        # Grape - عنب
        'grape': 'Grape',
        'grapes': 'Grape',
        'raisin': 'Grape',
        'عنب': 'Grape',
        
        # Fig - تين
        'fig': 'Fig',
        'figue': 'Fig',
        'تين': 'Fig',
        'كرموس': 'Fig',
        
        # Pomegranate - رمان
        'pomegranate': 'Pomegranate',
        'grenade': 'Pomegranate',
        'pomegranat': 'Pomegranate',
        'رمان': 'Pomegranate',
        'رمانة': 'Pomegranate',
        
        # Date - تمر
        'date': 'Date',
        'dates': 'Date',
        'datte': 'Date',
        'تمر': 'Date',
        'تمور': 'Date',
        
        # Apricot - مشمش
        'apricot': 'Apricot',
        'abricot': 'Apricot',
        'aprocot': 'Apricot',
        'مشمش': 'Apricot',
        
        # Peach - خوخ
        'peach': 'Peach',
        'peche': 'Peach',
        'pêche': 'Peach',
        'pech': 'Peach',
        'خوخ': 'Peach',
        'دراق': 'Peach',
        
        # Plum - برقوق
        'plum': 'Plum',
        'prune': 'Plum',
        'برقوق': 'Plum',
        
        # Cherry - كرز
        'cherry': 'Cherry',
        'cherries': 'Cherry',
        'cerise': 'Cherry',
        'chery': 'Cherry',
        'كرز': 'Cherry',
        'حب الملوك': 'Cherry',
        
        # Apple - تفاح
        'apple': 'Apple',
        'pomme': 'Apple',
        'aple': 'Apple',
        'تفاح': 'Apple',
        'تفاحة': 'Apple',
        
        # Pear - إجاص
        'pear': 'Pear',
        'poire': 'Pear',
        'pere': 'Pear',
        'إجاص': 'Pear',
        'كمثرى': 'Pear',
        
        # Banana - موز
        'banana': 'Banana',
        'banane': 'Banana',
        'bannana': 'Banana',
        'موز': 'Banana',
        'موزة': 'Banana',
        
        # Dairy - حليب
        'milk': 'Milk',
        'lait': 'Milk',
        'حليب': 'Milk',
        'لبن': 'Milk',
        
        'cheese': 'Cheese',
        'fromage': 'Cheese',
        'جبن': 'Cheese',
        'جبنة': 'Cheese',
        
        'yogurt': 'Yogurt',
        'yaourt': 'Yogurt',
        'ياغورت': 'Yogurt',
        'زبادي': 'Yogurt',
        'رايب': 'Yogurt',
        
        'butter': 'Butter',
        'beurre': 'Butter',
        'زبدة': 'Butter',
        
        # Honey - عسل
        'honey': 'Honey',
        'miel': 'Honey',
        'hony': 'Honey',
        'عسل': 'Honey',
    }
    
    # Normalize input
    normalized = normalize_for_matching(input_name)
    
    # Try exact match first (for Arabic)
    if input_name.strip() in name_variations:
        return name_variations[input_name.strip()]
    
    # Try normalized match
    if normalized in name_variations:
        return name_variations[normalized]
    
    # Try partial matching
    for variation, canonical in name_variations.items():
        if variation in normalized or normalized in variation:
            return canonical
    
    # If no match found, capitalize the input
    return input_name.strip().lower().capitalize()


def clean_text(text):
    """
    Clean and standardize product name.
    Uses canonical name dictionary.
    """
    if not text:
        return ''
    
    # Remove extra spaces
    cleaned = ' '.join(text.split())
    
    # Find canonical name
    canonical = find_canonical_name(cleaned)
    
    return canonical


def import_seasonal_data():
    """
    Import seasonal data from CSV file.
    Handles dirty data with:
    - Inconsistent capitalization
    - Extra whitespace
    - Duplicate entries
    - Typos and variations
    - Arabic/French/English names
    """
    
    # Path to CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'seasonal_data.csv')
    
    print(f"📂 Reading CSV file: {csv_path}")
    print("🧹 Cleaning and importing data...\n")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        return
    
    cursor = connection.cursor()
    
    imported = 0
    skipped = 0
    duplicates = 0
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (after header)
            try:
                # Extract data
                product_name = row.get('nom_produit', '').strip()
                start_month = row.get('mois_debut', '').strip()
                end_month = row.get('mois_fin', '').strip()
                
                # Skip empty rows
                if not product_name:
                    print(f"⚠️  Row {row_num}: Skipping empty product name")
                    skipped += 1
                    continue
                
                # Clean product name (handles typos, Arabic, French, English)
                product_clean = clean_text(product_name)
                
                # Convert months to integers
                try:
                    start = int(start_month)
                    end = int(end_month)
                except ValueError:
                    print(f"⚠️  Row {row_num}: Invalid month values for '{product_name}'")
                    skipped += 1
                    continue
                
                # Validate month ranges
                if not (1 <= start <= 12 and 1 <= end <= 12):
                    print(f"⚠️  Row {row_num}: Month out of range for '{product_name}'")
                    skipped += 1
                    continue
                
                # Show cleaning if name changed
                if product_name != product_clean:
                    print(f"🔧 Row {row_num}: '{product_name}' → '{product_clean}'")
                
                # Insert into database (ignore duplicates)
                cursor.execute("""
                    INSERT INTO product_seasons (product_name, start_month, end_month)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (product_name) DO NOTHING
                    RETURNING id
                """, [product_clean, start, end])
                
                result = cursor.fetchone()
                
                if result:
                    print(f"✅ Row {row_num}: Imported '{product_clean}' (season: {start}-{end})")
                    imported += 1
                else:
                    print(f"⏭️  Row {row_num}: Duplicate '{product_clean}' - skipped")
                    duplicates += 1
                
            except Exception as e:
                print(f"❌ Row {row_num}: Error - {e}")
                skipped += 1
    
    # Commit changes
    connection.commit()
    cursor.close()
    
    # Summary
    print("\n" + "="*60)
    print("📊 IMPORT SUMMARY")
    print("="*60)
    print(f"✅ Successfully imported:    {imported} products")
    print(f"⏭️  Duplicates skipped:      {duplicates} products")
    print(f"⚠️  Errors/empty rows:       {skipped} rows")
    print(f"📦 Total unique products:   {imported} in database")
    print("="*60)


if __name__ == '__main__':
    print("🌱 DZ-Fellah Seasonal Data Import Script")
    print("="*60)
    import_seasonal_data()
    print("\n✨ Import complete!")