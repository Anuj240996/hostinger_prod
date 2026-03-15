-- Fix django_content_type.id sequence
-- Similar to fix_django_migrations_id.sql

-- Ensure sequence exists (safe to rerun)
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM django_content_type;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'django_content_type_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE django_content_type_id_seq START %s', max_id + 1);
        RAISE NOTICE 'Created sequence django_content_type_id_seq starting at %', max_id + 1;
    ELSE
        EXECUTE format('SELECT setval(''django_content_type_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM django_content_type)))', max_id + 1);
        RAISE NOTICE 'Updated sequence django_content_type_id_seq';
    END IF;
END $$;

-- Set the default for id to use the sequence
ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq');

-- Verify
SELECT column_default 
FROM information_schema.columns 
WHERE table_name = 'django_content_type' 
AND column_name = 'id';
