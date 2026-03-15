-- Fix django_migrations table: ensure id column has a sequence/default
-- This fixes the "null value in column id" error when Django records migrations

-- Check if sequence exists, if not create it
DO $$
DECLARE
    max_id INTEGER;
    seq_name TEXT := 'django_migrations_id_seq';
BEGIN
    -- Get max id
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM django_migrations;
    
    -- Check if sequence exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = seq_name
    ) THEN
        -- Create sequence starting from max_id + 1
        EXECUTE format('CREATE SEQUENCE %I START %s', seq_name, max_id + 1);
        RAISE NOTICE 'Created sequence % starting at %', seq_name, max_id + 1;
    ELSE
        -- Update sequence to be at least max_id + 1
        EXECUTE format('SELECT setval(%L, GREATEST(%s, (SELECT last_value FROM %I)))', seq_name, max_id + 1, seq_name);
        RAISE NOTICE 'Updated sequence % to at least %', seq_name, max_id + 1;
    END IF;
    
    -- Set default for id column
    ALTER TABLE django_migrations ALTER COLUMN id SET DEFAULT nextval(seq_name);
    RAISE NOTICE 'Set default for id column';
END $$;

-- Verify
SELECT column_name, column_default 
FROM information_schema.columns 
WHERE table_name = 'django_migrations' AND column_name = 'id';
