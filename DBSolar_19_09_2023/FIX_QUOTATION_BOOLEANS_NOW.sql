-- QUICK FIX: Convert quotation_termsandcondition boolean fields
-- Run this SQL directly in your PostgreSQL database

-- Fix is_active column
ALTER TABLE quotation_termsandcondition 
ALTER COLUMN is_active TYPE boolean 
USING CASE 
    WHEN is_active::text = '1' OR is_active::text = 't' OR LOWER(is_active::text) = 'true' THEN true 
    WHEN is_active::text = '0' OR is_active::text = 'f' OR LOWER(is_active::text) = 'false' THEN false 
    ELSE false
END;

-- Fix has_yellow_background column  
ALTER TABLE quotation_termsandcondition 
ALTER COLUMN has_yellow_background TYPE boolean 
USING CASE 
    WHEN has_yellow_background::text = '1' OR has_yellow_background::text = 't' OR LOWER(has_yellow_background::text) = 'true' THEN true 
    WHEN has_yellow_background::text = '0' OR has_yellow_background::text = 'f' OR LOWER(has_yellow_background::text) = 'false' THEN false 
    ELSE false
END;

-- Verify
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'quotation_termsandcondition' 
AND column_name IN ('has_yellow_background', 'is_active');
