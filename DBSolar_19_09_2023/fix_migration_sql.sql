-- Direct SQL fix for migration history issue
-- Run this on your PostgreSQL database

-- Check current state
SELECT name, applied FROM django_migrations 
WHERE app = 'customer' AND (name LIKE '0045%' OR name LIKE '0046%')
ORDER BY applied;

-- If 0046 exists but 0045 doesn't, add 0045
INSERT INTO django_migrations (app, name, applied)
SELECT 'customer', '0045_merge_20260104_1419', 
       (SELECT applied - INTERVAL '1 second' FROM django_migrations 
        WHERE app = 'customer' AND name LIKE '0046%' LIMIT 1)
WHERE NOT EXISTS (
    SELECT 1 FROM django_migrations 
    WHERE app = 'customer' AND name = '0045_merge_20260104_1419'
);

-- If 0046 was applied before 0045, fix the timestamp
UPDATE django_migrations 
SET applied = (
    SELECT applied - INTERVAL '1 second' 
    FROM django_migrations 
    WHERE app = 'customer' AND name LIKE '0046%' LIMIT 1
)
WHERE app = 'customer' 
  AND name LIKE '0045%'
  AND EXISTS (
      SELECT 1 FROM django_migrations 
      WHERE app = 'customer' 
        AND name LIKE '0046%' 
        AND applied < django_migrations.applied
  );

-- Verify fix
SELECT name, applied FROM django_migrations 
WHERE app = 'customer' AND (name LIKE '0045%' OR name LIKE '0046%')
ORDER BY applied;

