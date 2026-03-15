-- Fix boolean fields in quotation_termsandcondition table
-- Run this SQL directly in your PostgreSQL database

-- Convert is_active from bit varying to boolean
ALTER TABLE quotation_termsandcondition 
ALTER COLUMN is_active TYPE boolean 
USING CASE 
    WHEN is_active::text IN ('1', 't', 'true', 'True', 'TRUE', 'y', 'yes', 'Y', 'YES') THEN true 
    WHEN is_active::text IN ('0', 'f', 'false', 'False', 'FALSE', 'n', 'no', 'N', 'NO', '') THEN false 
    ELSE false
END;

-- Convert has_yellow_background from bit varying to boolean
ALTER TABLE quotation_termsandcondition 
ALTER COLUMN has_yellow_background TYPE boolean 
USING CASE 
    WHEN has_yellow_background::text IN ('1', 't', 'true', 'True', 'TRUE', 'y', 'yes', 'Y', 'YES') THEN true 
    WHEN has_yellow_background::text IN ('0', 'f', 'false', 'False', 'FALSE', 'n', 'no', 'N', 'NO', '') THEN false 
    ELSE false
END;

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'quotation_termsandcondition' 
AND column_name IN ('is_active', 'has_yellow_background');
