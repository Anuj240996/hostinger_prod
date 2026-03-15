-- Fix sequence for quotation_otheritem table
-- This script creates a sequence and sets default for the id column

-- ============================================================
-- Fix quotation_otheritem
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_otheritem;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_otheritem_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_otheritem_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_otheritem_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_otheritem)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_otheritem 
ALTER COLUMN id SET DEFAULT nextval('quotation_otheritem_id_seq');

-- Initialize sequence if table is empty
SELECT setval('quotation_otheritem_id_seq', COALESCE((SELECT MAX(id) FROM quotation_otheritem), 0) + 1, false);

-- Verification
SELECT 
    sequencename,
    last_value
FROM pg_sequences
WHERE sequencename = 'quotation_otheritem_id_seq';

SELECT 
    'quotation_otheritem' as table_name,
    MAX(id) as max_id,
    COUNT(*) as total_rows
FROM quotation_otheritem;
