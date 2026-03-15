-- IMMEDIATE FIX for customer_controller id column
-- Copy and paste this ENTIRE block into your PostgreSQL database and run it

BEGIN;

-- Drop primary key if exists
ALTER TABLE customer_controller DROP CONSTRAINT IF EXISTS customer_controller_pkey;

-- Drop sequence if exists
DROP SEQUENCE IF EXISTS customer_controller_id_seq CASCADE;

-- Create new sequence
CREATE SEQUENCE customer_controller_id_seq;

-- Update any NULL id values
UPDATE customer_controller SET id = nextval('customer_controller_id_seq') WHERE id IS NULL;

-- Set sequence to max(id) + 1
SELECT setval('customer_controller_id_seq', COALESCE((SELECT MAX(id) FROM customer_controller), 0) + 1, false);

-- Set column to NOT NULL
ALTER TABLE customer_controller ALTER COLUMN id SET NOT NULL;

-- Set DEFAULT value (THIS IS THE KEY FIX!)
ALTER TABLE customer_controller ALTER COLUMN id SET DEFAULT nextval('customer_controller_id_seq');

-- Add primary key
ALTER TABLE customer_controller ADD CONSTRAINT customer_controller_pkey PRIMARY KEY (id);

-- Make sequence owned by column
ALTER SEQUENCE customer_controller_id_seq OWNED BY customer_controller.id;

COMMIT;

-- Verify it worked (should show default with nextval)
SELECT column_name, column_default, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'customer_controller' AND column_name = 'id';

