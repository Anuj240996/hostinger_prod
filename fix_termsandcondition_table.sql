-- Fix quotation_termsandcondition table structure
-- Add default values for bit varying columns and fix created_at type

-- ============================================================
-- 1. Add default values for bit varying columns
-- ============================================================
ALTER TABLE quotation_termsandcondition 
ALTER COLUMN has_yellow_background SET DEFAULT B'0'::bit varying;

ALTER TABLE quotation_termsandcondition 
ALTER COLUMN is_active SET DEFAULT B'1'::bit varying;

-- ============================================================
-- 2. Fix created_at column type (if it's text, convert to timestamptz)
-- ============================================================
-- First, check if we need to convert
DO $$
BEGIN
    -- Check if created_at is text type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'quotation_termsandcondition' 
        AND column_name = 'created_at' 
        AND data_type = 'text'
    ) THEN
        -- Convert text to timestamptz
        ALTER TABLE quotation_termsandcondition 
        ALTER COLUMN created_at TYPE timestamptz 
        USING CASE 
            WHEN created_at ~ '^\d{4}-\d{2}-\d{2}' THEN created_at::timestamptz
            ELSE now()
        END;
        
        -- Set default to now()
        ALTER TABLE quotation_termsandcondition 
        ALTER COLUMN created_at SET DEFAULT now();
    END IF;
END $$;

-- ============================================================
-- Verification
-- ============================================================
SELECT 
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'quotation_termsandcondition'
ORDER BY ordinal_position;
