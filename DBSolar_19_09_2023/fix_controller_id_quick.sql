-- Quick fix for customer_controller id column
-- Run this directly on your PostgreSQL database

-- Step 1: Drop primary key if exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'customer_controller_pkey'
    ) THEN
        ALTER TABLE customer_controller DROP CONSTRAINT customer_controller_pkey;
    END IF;
END $$;

-- Step 2: Drop and recreate sequence
DROP SEQUENCE IF EXISTS customer_controller_id_seq CASCADE;
CREATE SEQUENCE customer_controller_id_seq;

-- Step 3: Update NULL id values
UPDATE customer_controller 
SET id = nextval('customer_controller_id_seq') 
WHERE id IS NULL;

-- Step 4: Set sequence to max(id) + 1
SELECT setval('customer_controller_id_seq', 
    COALESCE((SELECT MAX(id) FROM customer_controller), 0) + 1, false);

-- Step 5: Set NOT NULL
ALTER TABLE customer_controller 
ALTER COLUMN id SET NOT NULL;

-- Step 6: Set DEFAULT
ALTER TABLE customer_controller 
ALTER COLUMN id SET DEFAULT nextval('customer_controller_id_seq');

-- Step 7: Add primary key
ALTER TABLE customer_controller 
ADD CONSTRAINT customer_controller_pkey PRIMARY KEY (id);

-- Step 8: Set sequence ownership
ALTER SEQUENCE customer_controller_id_seq OWNED BY customer_controller.id;

-- Verify
SELECT 
    column_name, 
    column_default, 
    is_nullable,
    data_type
FROM information_schema.columns 
WHERE table_name = 'customer_controller' 
AND column_name = 'id';

