-- Fix auth_user table to ensure it has a primary key constraint
-- This is required for foreign key references

-- Check if primary key exists, if not add it
DO $$
BEGIN
    -- Check if primary key constraint exists
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_constraint 
        WHERE conname = 'auth_user_pkey' 
        AND conrelid = 'auth_user'::regclass
    ) THEN
        -- Add primary key constraint on id column
        ALTER TABLE auth_user 
        ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);
        
        RAISE NOTICE 'Primary key constraint added to auth_user table';
    ELSE
        RAISE NOTICE 'Primary key constraint already exists on auth_user table';
    END IF;
END $$;

-- Verify the constraint was created
SELECT 
    constraint_name, 
    constraint_type,
    table_name
FROM information_schema.table_constraints 
WHERE table_name = 'auth_user' 
AND constraint_type = 'PRIMARY KEY';
