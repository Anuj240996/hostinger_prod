"""
Django management command to fix boolean fields in quotation_termsandcondition table.
Converts bit varying columns to boolean type.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix boolean fields in quotation_termsandcondition table by converting bit varying to boolean'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('FIXING QUOTATION BOOLEAN FIELDS')
        self.stdout.write('='*80)
        
        table_name = 'quotation_termsandcondition'
        
        with connection.cursor() as cursor:
            # Check current column types
            self.stdout.write('\nChecking current column types...')
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND column_name IN ('has_yellow_background', 'is_active')
            """, [table_name])
            
            columns = cursor.fetchall()
            self.stdout.write(f'\nCurrent column types in {table_name}:')
            for col_name, data_type in columns:
                self.stdout.write(f'  - {col_name}: {data_type}')
            
            # Fix has_yellow_background
            self.stdout.write('\n' + '-'*80)
            self.stdout.write('1. Converting has_yellow_background from bit varying to boolean...')
            try:
                cursor.execute("""
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'has_yellow_background';
                """, [table_name])
                result = cursor.fetchone()
                
                if not result:
                    self.stdout.write(self.style.WARNING('   ⚠ Column has_yellow_background not found, skipping...'))
                else:
                    data_type = result[0]
                    if data_type == 'boolean':
                        self.stdout.write(self.style.SUCCESS('   ✓ has_yellow_background is already boolean, skipping...'))
                    else:
                        cursor.execute(f"""
                            ALTER TABLE {table_name} 
                            ALTER COLUMN has_yellow_background TYPE boolean 
                            USING CASE 
                                WHEN has_yellow_background::text = '1' OR has_yellow_background::text = 't' OR has_yellow_background::text = 'true' THEN true 
                                WHEN has_yellow_background::text = '0' OR has_yellow_background::text = 'f' OR has_yellow_background::text = 'false' THEN false 
                                WHEN has_yellow_background IS NULL THEN NULL 
                                ELSE (has_yellow_background::text)::boolean 
                            END;
                        """)
                        self.stdout.write(self.style.SUCCESS('   ✓ has_yellow_background converted to boolean!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ ERROR: {str(e)}'))
            
            # Fix is_active
            self.stdout.write('\n' + '-'*80)
            self.stdout.write('2. Converting is_active from bit varying to boolean...')
            try:
                cursor.execute("""
                    SELECT data_type FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = 'is_active';
                """, [table_name])
                result = cursor.fetchone()
                
                if not result:
                    self.stdout.write(self.style.WARNING('   ⚠ Column is_active not found, skipping...'))
                else:
                    data_type = result[0]
                    if data_type == 'boolean':
                        self.stdout.write(self.style.SUCCESS('   ✓ is_active is already boolean, skipping...'))
                    else:
                        cursor.execute(f"""
                            ALTER TABLE {table_name} 
                            ALTER COLUMN is_active TYPE boolean 
                            USING CASE 
                                WHEN is_active::text = '1' OR is_active::text = 't' OR is_active::text = 'true' THEN true 
                                WHEN is_active::text = '0' OR is_active::text = 'f' OR is_active::text = 'false' THEN false 
                                WHEN is_active IS NULL THEN NULL 
                                ELSE (is_active::text)::boolean 
                            END;
                        """)
                        self.stdout.write(self.style.SUCCESS('   ✓ is_active converted to boolean!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ✗ ERROR: {str(e)}'))
            
            # Verify the changes
            self.stdout.write('\n' + '-'*80)
            self.stdout.write('3. Verifying column types...')
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND column_name IN ('has_yellow_background', 'is_active')
            """, [table_name])
            
            columns = cursor.fetchall()
            self.stdout.write(f'\nFinal column types in {table_name}:')
            all_ok = True
            for col_name, data_type in columns:
                if data_type == 'boolean':
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {col_name}: {data_type}'))
                else:
                    self.stdout.write(self.style.ERROR(f'  ✗ {col_name}: {data_type} (should be boolean)'))
                    all_ok = False
            
            self.stdout.write('\n' + '='*80)
            if all_ok:
                self.stdout.write(self.style.SUCCESS('FIX COMPLETE! All columns are now boolean type.'))
            else:
                self.stdout.write(self.style.WARNING('FIX COMPLETE! Some columns may still need attention.'))
            self.stdout.write('='*80)
            self.stdout.write('\nIMPORTANT: Restart your Django server if it\'s running!')
            self.stdout.write('='*80 + '\n')
