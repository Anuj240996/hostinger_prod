# Generated migration to fix id column in SolarPump and Controller models
# This ensures the id column has a proper sequence and primary key constraint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0014_alter_customer_cust_id'),  # Update this to your latest migration number
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Fix SolarPump table id column
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
                    ELSE
                        -- If id column doesn't exist, add it
                        ALTER TABLE customer_solarpump 
                        ADD COLUMN id SERIAL PRIMARY KEY;
                    END IF;
                END $$;
                
                -- Fix Controller table id column
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
                    ELSE
                        -- If id column doesn't exist, add it
                        ALTER TABLE customer_controller 
                        ADD COLUMN id SERIAL PRIMARY KEY;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                -- Reverse migration (if needed)
                -- Note: This won't actually reverse the changes, but provides a placeholder
                SELECT 1;
            """
        ),
    ]

