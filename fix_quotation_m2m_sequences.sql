-- Fix sequences for all quotation many-to-many junction tables
-- This script creates sequences and sets defaults for all M2M relationship tables

-- ============================================================
-- 1. Fix quotation_quotation_panel_companies
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_quotation_panel_companies;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_quotation_panel_companies_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_quotation_panel_companies_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_quotation_panel_companies_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_quotation_panel_companies)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_quotation_panel_companies 
ALTER COLUMN id SET DEFAULT nextval('quotation_quotation_panel_companies_id_seq');

-- ============================================================
-- 2. Fix quotation_quotation_inverter_companies
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_quotation_inverter_companies;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_quotation_inverter_companies_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_quotation_inverter_companies_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_quotation_inverter_companies_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_quotation_inverter_companies)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_quotation_inverter_companies 
ALTER COLUMN id SET DEFAULT nextval('quotation_quotation_inverter_companies_id_seq');

-- ============================================================
-- 3. Fix quotation_quotation_representatives
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_quotation_representatives;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_quotation_representatives_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_quotation_representatives_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_quotation_representatives_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_quotation_representatives)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_quotation_representatives 
ALTER COLUMN id SET DEFAULT nextval('quotation_quotation_representatives_id_seq');

-- ============================================================
-- 4. Fix quotation_quotation_terms_conditions
-- ============================================================
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM quotation_quotation_terms_conditions;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'quotation_quotation_terms_conditions_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE quotation_quotation_terms_conditions_id_seq START %s', max_id + 1);
    ELSE
        EXECUTE format('SELECT setval(''quotation_quotation_terms_conditions_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM quotation_quotation_terms_conditions)))', max_id + 1);
    END IF;
END $$;

ALTER TABLE quotation_quotation_terms_conditions 
ALTER COLUMN id SET DEFAULT nextval('quotation_quotation_terms_conditions_id_seq');

-- ============================================================
-- Verification: Show all sequences created
-- ============================================================
SELECT 
    schemaname,
    sequencename,
    last_value
FROM pg_sequences
WHERE sequencename LIKE 'quotation_quotation_%_id_seq'
ORDER BY sequencename;
