-- Complete fix for customer_solarpump and customer_controller id column issues
-- This script will ensure the id columns have proper sequence and default values

-- Step 1: Drop existing constraints if they exist (to avoid conflicts)
DO $$
BEGIN
    -- Drop primary key constraint if it exists
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'customer_solarpump_pkey'
    ) THEN
        ALTER TABLE customer_solarpump DROP CONSTRAINT customer_solarpump_pkey;
    END IF;
END $$;

-- Step 2: Drop the sequence if it exists (we'll recreate it)
DROP SEQUENCE IF EXISTS customer_solarpump_id_seq CASCADE;

-- Step 3: Check if id column exists, if not create it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_solarpump' 
        AND column_name = 'id'
    ) THEN
        ALTER TABLE customer_solarpump ADD COLUMN id INTEGER;
    END IF;
END $$;

-- Step 4: Create the sequence
CREATE SEQUENCE IF NOT EXISTS customer_solarpump_id_seq;

-- Step 5: Update existing NULL id values
UPDATE customer_solarpump 
SET id = nextval('customer_solarpump_id_seq') 
WHERE id IS NULL;

-- Step 6: Set the sequence to start from max(id) + 1
SELECT setval('customer_solarpump_id_seq', COALESCE((SELECT MAX(id) FROM customer_solarpump), 0) + 1, false);

-- Step 7: Set the column to NOT NULL
ALTER TABLE customer_solarpump 
ALTER COLUMN id SET NOT NULL;

-- Step 8: Set the default value to use the sequence
ALTER TABLE customer_solarpump 
ALTER COLUMN id SET DEFAULT nextval('customer_solarpump_id_seq');

-- Step 9: Add primary key constraint
ALTER TABLE customer_solarpump 
ADD CONSTRAINT customer_solarpump_pkey PRIMARY KEY (id);

-- Step 10: Make sure the sequence is owned by the column
ALTER SEQUENCE customer_solarpump_id_seq OWNED BY customer_solarpump.id;

-- Verify the fix for customer_solarpump
SELECT 
    column_name, 
    column_default, 
    is_nullable,
    data_type
FROM information_schema.columns 
WHERE table_name = 'customer_solarpump' 
AND column_name = 'id';

-- Fix customer_controller table id column
-- Step 1: Drop existing constraints if they exist (to avoid conflicts)
DO $$
BEGIN
    -- Drop primary key constraint if it exists
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'customer_controller_pkey'
    ) THEN
        ALTER TABLE customer_controller DROP CONSTRAINT customer_controller_pkey;
    END IF;
END $$;

-- Step 2: Drop the sequence if it exists (we'll recreate it)
DROP SEQUENCE IF EXISTS customer_controller_id_seq CASCADE;

-- Step 3: Check if id column exists, if not create it
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

-- Step 4: Create the sequence
CREATE SEQUENCE IF NOT EXISTS customer_controller_id_seq;

-- Step 5: Update existing NULL id values
UPDATE customer_controller 
SET id = nextval('customer_controller_id_seq') 
WHERE id IS NULL;

-- Step 6: Set the sequence to start from max(id) + 1
SELECT setval('customer_controller_id_seq', COALESCE((SELECT MAX(id) FROM customer_controller), 0) + 1, false);

-- Step 7: Set the column to NOT NULL
ALTER TABLE customer_controller 
ALTER COLUMN id SET NOT NULL;

-- Step 8: Set the default value to use the sequence
ALTER TABLE customer_controller 
ALTER COLUMN id SET DEFAULT nextval('customer_controller_id_seq');

-- Step 9: Add primary key constraint
ALTER TABLE customer_controller 
ADD CONSTRAINT customer_controller_pkey PRIMARY KEY (id);

-- Step 10: Make sure the sequence is owned by the column
ALTER SEQUENCE customer_controller_id_seq OWNED BY customer_controller.id;

-- Verify the fix for customer_controller
SELECT 
    column_name, 
    column_default, 
    is_nullable,
    data_type
FROM information_schema.columns 
WHERE table_name = 'customer_controller' 
AND column_name = 'id';

