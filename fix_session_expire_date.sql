-- Fix django_session.expire_date column type
-- Convert from text to timestamp with time zone

-- First, check current type
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'django_session' AND column_name = 'expire_date';

-- Convert the column type
ALTER TABLE django_session 
ALTER COLUMN expire_date TYPE timestamp with time zone 
USING expire_date::timestamp with time zone;

-- Verify the fix
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'django_session' AND column_name = 'expire_date';
