from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import sys
import re

class Command(BaseCommand):
    help = 'Execute SQL schema files from db/schema/ to create database tables'

    def split_sql_statements(self, sql):
        """
        Split SQL into statements, handling $$ delimiters for functions/procedures
        """
        statements = []
        current = []
        in_dollar_quote = False
        dollar_tag = None
        
        lines = sql.split('\n')
        
        for line in lines:
            # Check for $$ or $tag$ delimiter
            dollar_matches = re.findall(r'\$(\w*)\$', line)
            
            for match in dollar_matches:
                tag = f'${match}$'
                if not in_dollar_quote:
                    in_dollar_quote = True
                    dollar_tag = tag
                elif tag == dollar_tag:
                    in_dollar_quote = False
                    dollar_tag = None
            
            current.append(line)
            
            # Only split on ; if we're not inside a $$ block
            if not in_dollar_quote and line.strip().endswith(';'):
                stmt = '\n'.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
        
        # Add any remaining content
        if current:
            stmt = '\n'.join(current).strip()
            if stmt:
                statements.append(stmt)
        
        return statements

    def handle(self, *args, **options):
        # Path to your schema directory
        schema_dir = Path('db/schemas')
        
        if not schema_dir.exists():
            self.stdout.write(self.style.ERROR(f'❌ Schema directory not found: {schema_dir}'))
            self.stdout.write(self.style.WARNING('Make sure you are running this from the project root (where manage.py is)'))
            sys.exit(1)
        
        # Get all .sql files sorted by name
        sql_files = sorted(schema_dir.glob('*.sql'))
        
        if not sql_files:
            self.stdout.write(self.style.ERROR('❌ No SQL files found in db/schema/'))
            sys.exit(1)
        
        self.stdout.write(self.style.WARNING(f'\n📁 Found {len(sql_files)} SQL file(s) to execute:\n'))
        for f in sql_files:
            self.stdout.write(f'   • {f.name}')
        
        self.stdout.write('\n' + '='*60)
        
        success_count = 0
        error_count = 0
        
        for sql_file in sql_files:
            self.stdout.write(f'\n🔄 Executing {sql_file.name}...')
            
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql = f.read()
                
                # Use improved statement splitting
                statements = self.split_sql_statements(sql)
                
                with connection.cursor() as cursor:
                    for statement in statements:
                        if statement.strip():
                            cursor.execute(statement)
                
                self.stdout.write(self.style.SUCCESS(f'   ✓ Successfully executed {sql_file.name}'))
                success_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ Error in {sql_file.name}:'))
                self.stdout.write(self.style.ERROR(f'      {str(e)}'))
                error_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✓ Success: {success_count} file(s)'))
        
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ Failed: {error_count} file(s)'))
            self.stdout.write(self.style.WARNING('\n⚠️  Some files failed to execute. Check the errors above.'))
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS('\n🎉 All schema files executed successfully!'))
            self.stdout.write(self.style.SUCCESS('Your database tables are now created.\n'))