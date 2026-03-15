"""
Django management command to fix the id column in customer_solarpump and customer_controller tables.
This command creates sequences and sets up proper defaults for the id columns.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix the id column in customer_solarpump and customer_controller tables by creating sequences and setting defaults'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('Fixing customer_solarpump table...')
            
            # Fix SolarPump table
            cursor.execute("""
                DO $$
                BEGIN
                    -- Check if id column exists
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'public'
                        AND table_name = 'customer_solarpump' 
                        AND column_name = 'id'
                    ) THEN
                        -- Check if sequence exists, if not create it
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_sequences 
                            WHERE schemaname = 'public' 
                            AND sequencename = 'customer_solarpump_id_seq'
                        ) THEN
                            CREATE SEQUENCE customer_solarpump_id_seq;
                            RAISE NOTICE 'Created sequence customer_solarpump_id_seq';
                        END IF;
                        
                        -- Set the sequence as default for id column
                        ALTER TABLE customer_solarpump 
                        ALTER COLUMN id SET DEFAULT nextval('customer_solarpump_id_seq');
                        
                        -- Update any NULL id values with sequence values
                        UPDATE customer_solarpump 
                        SET id = nextval('customer_solarpump_id_seq') 
                        WHERE id IS NULL;
                        
                        -- Set id as NOT NULL if it isn't already
                        ALTER TABLE customer_solarpump 
                        ALTER COLUMN id SET NOT NULL;
                        
                        -- Add primary key constraint if it doesn't exist
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'customer_solarpump_pkey'
                        ) THEN
                            ALTER TABLE customer_solarpump 
                            ADD CONSTRAINT customer_solarpump_pkey PRIMARY KEY (id);
                        END IF;
                        
                        -- Set the sequence to start from the max id + 1
                        SELECT setval('customer_solarpump_id_seq', COALESCE((SELECT MAX(id) FROM customer_solarpump), 0) + 1, false);
                        
                        RAISE NOTICE 'Fixed customer_solarpump table successfully';
                    ELSE
                        -- If id column doesn't exist, add it
                        ALTER TABLE customer_solarpump 
                        ADD COLUMN id SERIAL PRIMARY KEY;
                        RAISE NOTICE 'Added id column to customer_solarpump table';
                    END IF;
                END $$;
            """)
            
            self.stdout.write(self.style.SUCCESS('✓ Fixed customer_solarpump table'))
            
            self.stdout.write('Fixing customer_controller table...')
            
            # Fix Controller table
            cursor.execute("""
                DO $$
                BEGIN
                    -- Check if id column exists
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'public'
                        AND table_name = 'customer_controller' 
                        AND column_name = 'id'
                    ) THEN
                        -- Check if sequence exists, if not create it
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_sequences 
                            WHERE schemaname = 'public' 
                            AND sequencename = 'customer_controller_id_seq'
                        ) THEN
                            CREATE SEQUENCE customer_controller_id_seq;
                            RAISE NOTICE 'Created sequence customer_controller_id_seq';
                        END IF;
                        
                        -- Set the sequence as default for id column
                        ALTER TABLE customer_controller 
                        ALTER COLUMN id SET DEFAULT nextval('customer_controller_id_seq');
                        
                        -- Update any NULL id values with sequence values
                        UPDATE customer_controller 
                        SET id = nextval('customer_controller_id_seq') 
                        WHERE id IS NULL;
                        
                        -- Set id as NOT NULL if it isn't already
                        ALTER TABLE customer_controller 
                        ALTER COLUMN id SET NOT NULL;
                        
                        -- Add primary key constraint if it doesn't exist
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_constraint 
                            WHERE conname = 'customer_controller_pkey'
                        ) THEN
                            ALTER TABLE customer_controller 
                            ADD CONSTRAINT customer_controller_pkey PRIMARY KEY (id);
                        END IF;
                        
                        -- Set the sequence to start from the max id + 1
                        SELECT setval('customer_controller_id_seq', COALESCE((SELECT MAX(id) FROM customer_controller), 0) + 1, false);
                        
                        RAISE NOTICE 'Fixed customer_controller table successfully';
                    ELSE
                        -- If id column doesn't exist, add it
                        ALTER TABLE customer_controller 
                        ADD COLUMN id SERIAL PRIMARY KEY;
                        RAISE NOTICE 'Added id column to customer_controller table';
                    END IF;
                END $$;
            """)
            
            self.stdout.write(self.style.SUCCESS('✓ Fixed customer_controller table'))
            
            # Also mark migration 0028 as applied if it's not already
            self.stdout.write('Checking migration status...')
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('customer', '0028_fix_solarpump_controller_id', NOW())
                ON CONFLICT DO NOTHING;
            """)
            
            self.stdout.write(self.style.SUCCESS('✓ Migration status updated'))
            self.stdout.write(self.style.SUCCESS('\nAll fixes applied successfully!'))
            self.stdout.write('You can now try creating solar pump entries again.')

