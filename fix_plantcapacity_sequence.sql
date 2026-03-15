-- Fix sequence for quotation_plantcapacity table
-- This script creates a sequence and sets default for the id column

-- ============================================================
-- Fix quotation_plantcapacity
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_plantcapacity;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_plantcapacity_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_plantcapacity_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_plantcapacity_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_plantcapacity)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_plantcapacity 
ALTER COLUMN id SET DEFAULT nextval('quotation_plantcapacity_id_seq');

-- Initialize sequence if table is empty
SELECT setval('quotation_plantcapacity_id_seq', COALESCE((SELECT MAX(id) FROM quotation_plantcapacity), 0) + 1, false);

-- Verification
SELECT 
    sequencename,
    last_value
FROM pg_sequences
WHERE sequencename = 'quotation_plantcapacity_id_seq';

SELECT 
    'quotation_plantcapacity' as table_name,
    MAX(id) as max_id,
    COUNT(*) as total_rows
FROM quotation_plantcapacity;
