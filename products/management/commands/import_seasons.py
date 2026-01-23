"""
Django management command to import seasonal data
Usage: python manage.py import_seasons
"""

from django.core.management.base import BaseCommand
from django.db import connection
import csv
import os


class Command(BaseCommand):
    help = 'Import seasonal data from CSV - keeps original names for academic purposes'

    def handle(self, *args, **options):
        csv_path = os.path.join(os.path.dirname(__file__), '../../../scripts/seasonal_data.csv')
        
        self.stdout.write('🌱 DZ-Fellah Seasonal Data Import')
        self.stdout.write('='*60)
        self.stdout.write(f'📂 Reading: {csv_path}')
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'❌ CSV file not found!'))
            return
        
        cursor = connection.cursor()
        imported = 0
        skipped = 0
        duplicates = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    product_name = row.get('nom_produit', '').strip()
                    start_month = row.get('mois_debut', '').strip()
                    end_month = row.get('mois_fin', '').strip()
                    
                    if not product_name:
                        skipped += 1
                        continue
                    
                    # Keep original name, just clean whitespace
                    product_clean = ' '.join(product_name.split())
                    
                    try:
                        start = int(start_month)
                        end = int(end_month)
                    except ValueError:
                        self.stdout.write(f'⚠️  Row {row_num}: Invalid months')
                        skipped += 1
                        continue
                    
                    if not (1 <= start <= 12 and 1 <= end <= 12):
                        skipped += 1
                        continue
                    
                    cursor.execute("""
                        INSERT INTO product_seasons (product_name, start_month, end_month)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (product_name) DO NOTHING
                        RETURNING id
                    """, [product_clean, start, end])
                    
                    result = cursor.fetchone()
                    
                    if result:
                        self.stdout.write(f'✅ Row {row_num}: "{product_clean}" (season: {start}-{end})')
                        imported += 1
                    else:
                        self.stdout.write(f'⏭️  Row {row_num}: Duplicate "{product_clean}"')
                        duplicates += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Row {row_num}: {e}'))
                    skipped += 1
        
        connection.commit()
        cursor.close()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 IMPORT SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'✅ Imported:    {imported} products')
        self.stdout.write(f'⏭️  Duplicates:  {duplicates} products')
        self.stdout.write(f'⚠️  Skipped:     {skipped} rows')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('✨ Import complete!'))
