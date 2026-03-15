-- Fix boolean fields in quotation_termsandcondition table
-- Converts bit varying columns to boolean type

-- Fix has_yellow_background column
ALTER TABLE quotation_termsandcondition 
ADD COLUMN has_yellow_background_temp BOOLEAN DEFAULT FALSE;

UPDATE quotation_termsandcondition 
SET has_yellow_background_temp = CASE 
    WHEN has_yellow_background::text = '1' OR has_yellow_background::text = 't' THEN TRUE
    WHEN has_yellow_background::text = '0' OR has_yellow_background::text = 'f' THEN FALSE
    ELSE FALSE
END;

ALTER TABLE quotation_termsandcondition 
DROP COLUMN has_yellow_background;

ALTER TABLE quotation_termsandcondition 
RENAME COLUMN has_yellow_background_temp TO has_yellow_background;

-- Fix is_active column
ALTER TABLE quotation_termsandcondition 
ADD COLUMN is_active_temp BOOLEAN DEFAULT TRUE;

UPDATE quotation_termsandcondition 
SET is_active_temp = CASE 
    WHEN is_active::text = '1' OR is_active::text = 't' THEN TRUE
    WHEN is_active::text = '0' OR is_active::text = 'f' THEN FALSE
    ELSE TRUE
END;

ALTER TABLE quotation_termsandcondition 
DROP COLUMN is_active;

ALTER TABLE quotation_termsandcondition 
RENAME COLUMN is_active_temp TO is_active;

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'quotation_termsandcondition' 
AND column_name IN ('has_yellow_background', 'is_active');
