-- Fix quotation_quotation.id sequence issue
-- This script ensures the id column has a proper sequence for auto-increment

-- Step 1: Get the current max ID
DO $$
DECLARE
    max_id INTEGER;
    seq_name TEXT := 'quotation_quotation_id_seq';
BEGIN
    -- Get the maximum ID from the table
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_quotation;
    
    -- Step 2: Create sequence if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = seq_name) THEN
        EXECUTE format('CREATE SEQUENCE %I START %s', seq_name, max_id + 1);
        RAISE NOTICE 'Created sequence % starting at %', seq_name, max_id + 1;
    ELSE
        -- Update sequence to be at least max_id + 1
        EXECUTE format('SELECT setval(''%I'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_quotation)))', seq_name, max_id + 1);
        RAISE NOTICE 'Updated sequence % to start at %', seq_name, max_id + 1;
    END IF;
END $$;

-- Step 3: Make the id column use the sequence as default
-- First, check if the column is already an IDENTITY column or has a default
DO $$
DECLARE
    is_identity BOOLEAN;
    has_default BOOLEAN;
BEGIN
    -- Check if column is IDENTITY
    SELECT EXISTS (
        SELECT 1 FROM pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        WHERE c.relname = 'quotation_quotation'
        AND a.attname = 'id'
        AND a.attidentity != ''
    ) INTO is_identity;
    
    -- Check if column has a default
    SELECT EXISTS (
        SELECT 1 FROM pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        WHERE c.relname = 'quotation_quotation'
        AND a.attname = 'id'
        AND a.atthasdef
    ) INTO has_default;
    
    -- If not IDENTITY and no default, set the default
    IF NOT is_identity AND NOT has_default THEN
        ALTER TABLE quotation_quotation 
        ALTER COLUMN id SET DEFAULT nextval('quotation_quotation_id_seq');
        RAISE NOTICE 'Set default for id column to use sequence';
    ELSIF is_identity THEN
        RAISE NOTICE 'Column is already an IDENTITY column';
    ELSIF has_default THEN
        RAISE NOTICE 'Column already has a default value';
    END IF;
END $$;

-- Step 4: Ensure the sequence is owned by the column (for proper cleanup)
ALTER SEQUENCE IF EXISTS quotation_quotation_id_seq OWNED BY quotation_quotation.id;

-- Verify the fix
SELECT 
    column_name,
    column_default,
    is_nullable,
    data_type
FROM information_schema.columns
WHERE table_name = 'quotation_quotation' 
AND column_name = 'id';
