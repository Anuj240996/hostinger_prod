-- Fix sequences for all quotation-related tables that might be missing them
-- This script creates sequences and sets defaults for id columns

-- ============================================================
-- 1. Fix quotation_solarpanelcompany
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_solarpanelcompany;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_solarpanelcompany_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_solarpanelcompany_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_solarpanelcompany_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_solarpanelcompany)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_solarpanelcompany 
ALTER COLUMN id SET DEFAULT nextval('quotation_solarpanelcompany_id_seq');

SELECT setval('quotation_solarpanelcompany_id_seq', COALESCE((SELECT MAX(id) FROM quotation_solarpanelcompany), 0) + 1, false);

-- ============================================================
-- 2. Fix quotation_invertercompany
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_invertercompany;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_invertercompany_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_invertercompany_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_invertercompany_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_invertercompany)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_invertercompany 
ALTER COLUMN id SET DEFAULT nextval('quotation_invertercompany_id_seq');

SELECT setval('quotation_invertercompany_id_seq', COALESCE((SELECT MAX(id) FROM quotation_invertercompany), 0) + 1, false);

-- ============================================================
-- 3. Fix quotation_representative
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_representative;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_representative_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_representative_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_representative_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_representative)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_representative 
ALTER COLUMN id SET DEFAULT nextval('quotation_representative_id_seq');

SELECT setval('quotation_representative_id_seq', COALESCE((SELECT MAX(id) FROM quotation_representative), 0) + 1, false);

-- ============================================================
-- 4. Fix quotation_termsandcondition
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_termsandcondition;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_termsandcondition_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_termsandcondition_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_termsandcondition_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_termsandcondition)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_termsandcondition 
ALTER COLUMN id SET DEFAULT nextval('quotation_termsandcondition_id_seq');

SELECT setval('quotation_termsandcondition_id_seq', COALESCE((SELECT MAX(id) FROM quotation_termsandcondition), 0) + 1, false);

-- ============================================================
-- Verification: Show all sequences created
-- ============================================================
SELECT 
    sequencename,
    last_value
FROM pg_sequences
WHERE sequencename LIKE 'quotation_%_id_seq'
ORDER BY sequencename;
