-- Fix auth_permission.id sequence
-- Similar to fix_django_migrations_id.sql and fix_django_content_type_id.sql

-- Ensure sequence exists (safe to rerun)
DO $$
DECLARE max_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM auth_permission;
    
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'auth_permission_id_seq') THEN
        EXECUTE format('CREATE SEQUENCE auth_permission_id_seq START %s', max_id + 1);
        RAISE NOTICE 'Created sequence auth_permission_id_seq starting at %', max_id + 1;
    ELSE
        EXECUTE format('SELECT setval(''auth_permission_id_seq'', GREATEST(%s, (SELECT COALESCE(MAX(id),0)+1 FROM auth_permission)))', max_id + 1);
        RAISE NOTICE 'Updated sequence auth_permission_id_seq';
    END IF;
END $$;

-- Set the default for id to use the sequence
ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq');

-- Verify
SELECT column_default 
FROM information_schema.columns 
WHERE table_name = 'auth_permission' 
AND column_name = 'id';
