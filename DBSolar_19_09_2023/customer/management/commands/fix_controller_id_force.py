"""
Django management command to forcefully fix the id column in customer_controller table.
This will drop and recreate the sequence and default value to ensure it works.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Forcefully fix the id column in customer_controller table by recreating sequence and default'

    def handle(self, *args, **options):
        self.stdout.write('Starting forceful fix of customer_controller id column...')
        
        with connection.cursor() as cursor:
            try:
                # Step 1: Drop primary key constraint if exists
                self.stdout.write('Step 1: Dropping existing primary key constraint...')
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'customer_controller_pkey'
                        ) THEN
                            ALTER TABLE customer_controller DROP CONSTRAINT customer_controller_pkey;
                        END IF;
                    END $$;
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Dropped primary key constraint'))
                
                # Step 2: Drop sequence if exists
                self.stdout.write('Step 2: Dropping existing sequence...')
                cursor.execute("DROP SEQUENCE IF EXISTS customer_controller_id_seq CASCADE;")
                self.stdout.write(self.style.SUCCESS('  ✓ Dropped sequence'))
                
                # Step 3: Ensure id column exists
                self.stdout.write('Step 3: Ensuring id column exists...')
                cursor.execute("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'public'
                            AND table_name = 'customer_controller' 
                            AND column_name = 'id'
                        ) THEN
                            ALTER TABLE customer_controller ADD COLUMN id INTEGER;
                        END IF;
                    END $$;
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Id column exists'))
                
                # Step 4: Create new sequence
                self.stdout.write('Step 4: Creating new sequence...')
                cursor.execute("CREATE SEQUENCE customer_controller_id_seq;")
                self.stdout.write(self.style.SUCCESS('  ✓ Created sequence'))
                
                # Step 5: Update NULL id values
                self.stdout.write('Step 5: Updating NULL id values...')
                cursor.execute("""
                    UPDATE customer_controller 
                    SET id = nextval('customer_controller_id_seq') 
                    WHERE id IS NULL;
                """)
                updated_count = cursor.rowcount
                self.stdout.write(self.style.SUCCESS(f'  ✓ Updated {updated_count} NULL id values'))
                
                # Step 6: Set sequence to max(id) + 1
                self.stdout.write('Step 6: Setting sequence value...')
                cursor.execute("""
                    SELECT setval('customer_controller_id_seq', 
                        COALESCE((SELECT MAX(id) FROM customer_controller), 0) + 1, false);
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Set sequence value'))
                
                # Step 7: Set NOT NULL
                self.stdout.write('Step 7: Setting id column to NOT NULL...')
                cursor.execute("ALTER TABLE customer_controller ALTER COLUMN id SET NOT NULL;")
                self.stdout.write(self.style.SUCCESS('  ✓ Set NOT NULL'))
                
                # Step 8: Set default value
                self.stdout.write('Step 8: Setting default value to use sequence...')
                cursor.execute("""
                    ALTER TABLE customer_controller 
                    ALTER COLUMN id SET DEFAULT nextval('customer_controller_id_seq');
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Set default value'))
                
                # Step 9: Add primary key
                self.stdout.write('Step 9: Adding primary key constraint...')
                cursor.execute("""
                    ALTER TABLE customer_controller 
                    ADD CONSTRAINT customer_controller_pkey PRIMARY KEY (id);
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Added primary key'))
                
                # Step 10: Make sequence owned by column
                self.stdout.write('Step 10: Making sequence owned by column...')
                cursor.execute("ALTER SEQUENCE customer_controller_id_seq OWNED BY customer_controller.id;")
                self.stdout.write(self.style.SUCCESS('  ✓ Sequence ownership set'))
                
                # Verify
                self.stdout.write('Verifying the fix...')
                cursor.execute("""
                    SELECT 
                        column_name, 
                        column_default, 
                        is_nullable,
                        data_type
                    FROM information_schema.columns 
                    WHERE table_name = 'customer_controller' 
                    AND column_name = 'id';
                """)
                result = cursor.fetchone()
                if result:
                    col_name, col_default, is_nullable, data_type = result
                    self.stdout.write(f'\nColumn Details:')
                    self.stdout.write(f'  Name: {col_name}')
                    self.stdout.write(f'  Default: {col_default}')
                    self.stdout.write(f'  Nullable: {is_nullable}')
                    self.stdout.write(f'  Type: {data_type}')
                    
                    if 'nextval' in str(col_default) and is_nullable == 'NO':
                        self.stdout.write(self.style.SUCCESS('\n✓ Fix successful! The id column is now properly configured.'))
                    else:
                        self.stdout.write(self.style.WARNING('\n⚠ Warning: Column configuration may not be correct.'))
                
                self.stdout.write(self.style.SUCCESS('\n' + '='*50))
                self.stdout.write(self.style.SUCCESS('All fixes applied successfully!'))
                self.stdout.write(self.style.SUCCESS('You can now try creating controller entries again.'))
                self.stdout.write(self.style.SUCCESS('='*50))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n✗ Error occurred: {str(e)}'))
                raise

