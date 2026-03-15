-- Fix migration dependency issue
-- Migration 0020 was applied before 0019, but 0020 depends on 0019
-- This script fixes the django_migrations table directly

-- First, check current state
SELECT app, name, applied 
FROM django_migrations 
WHERE app = 'customer' 
AND name IN ('0019_alter_controller_assignby_alter_controller_assignto_and_more', '0020_alter_customer_cust_id')
ORDER BY applied;

-- Check if 0019 exists
SELECT COUNT(*) as count_0019
FROM django_migrations 
WHERE app = 'customer' 
AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';

-- Get 0020's timestamp
SELECT applied as applied_0020
FROM django_migrations 
WHERE app = 'customer' 
AND name = '0020_alter_customer_cust_id';

-- Fix: Insert 0019 if it doesn't exist, or update its timestamp if it's after 0020
DO $$
DECLARE
    count_0019 INTEGER;
    applied_0020 TIMESTAMP;
    applied_0019 TIMESTAMP;
BEGIN
    -- Check if 0019 exists
    SELECT COUNT(*) INTO count_0019
    FROM django_migrations 
    WHERE app = 'customer' 
    AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';
    
    -- Get 0020's timestamp
    SELECT applied INTO applied_0020
    FROM django_migrations 
    WHERE app = 'customer' 
    AND name = '0020_alter_customer_cust_id'
    LIMIT 1;
    
    IF count_0019 = 0 THEN
        -- 0019 doesn't exist - insert it with timestamp 1 minute before 0020
        INSERT INTO django_migrations (app, name, applied)
        VALUES ('customer', '0019_alter_controller_assignby_alter_controller_assignto_and_more', applied_0020 - INTERVAL '1 minute');
        RAISE NOTICE 'Inserted migration 0019 with timestamp %', applied_0020 - INTERVAL '1 minute';
    ELSE
        -- 0019 exists - check if its timestamp is after 0020
        SELECT applied INTO applied_0019
        FROM django_migrations 
        WHERE app = 'customer' 
        AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more'
        LIMIT 1;
        
        IF applied_0019 > applied_0020 THEN
            -- Update 0019's timestamp to be before 0020
            UPDATE django_migrations 
            SET applied = applied_0020 - INTERVAL '1 minute'
            WHERE app = 'customer' 
            AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';
            RAISE NOTICE 'Updated migration 0019 timestamp to %', applied_0020 - INTERVAL '1 minute';
        ELSE
            RAISE NOTICE 'Migration order is already correct';
        END IF;
    END IF;
END $$;

-- Verify the fix
SELECT app, name, applied 
FROM django_migrations 
WHERE app = 'customer' 
AND name IN ('0019_alter_controller_assignby_alter_controller_assignto_and_more', '0020_alter_customer_cust_id')
ORDER BY applied;
