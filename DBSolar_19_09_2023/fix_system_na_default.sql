-- Fix system_na column to have a default value
-- This allows Django to insert records without specifying system_na, then we update it

-- Step 1: Set default value for system_na column
ALTER TABLE quotation_quotation 
ALTER COLUMN system_na SET DEFAULT B'0'::bit varying;

-- Verify the change
SELECT 
    column_name,
    column_default,
    is_nullable,
    data_type
FROM information_schema.columns
WHERE table_name = 'quotation_quotation' 
AND column_name = 'system_na';
