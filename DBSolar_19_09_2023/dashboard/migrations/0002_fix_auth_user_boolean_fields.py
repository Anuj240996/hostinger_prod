# Generated migration to fix boolean field types in auth_user table
# This fixes the issue where boolean fields were stored as bit varying instead of boolean
# after migrating from SQLite to PostgreSQL

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Convert is_staff from bit varying/integer to boolean
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'public'
                        AND table_name = 'auth_user' 
                        AND column_name = 'is_staff'
                        AND data_type != 'boolean'
                    ) THEN
                        ALTER TABLE auth_user 
                        ALTER COLUMN is_staff TYPE boolean 
                        USING CASE 
                            WHEN is_staff::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
                            WHEN is_staff::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
                            ELSE false
                        END;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE auth_user 
                ALTER COLUMN is_staff TYPE integer USING CASE WHEN is_staff THEN 1 ELSE 0 END;
            """
        ),
        migrations.RunSQL(
            # Convert is_active from bit varying/integer to boolean
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'public'
                        AND table_name = 'auth_user' 
                        AND column_name = 'is_active'
                        AND data_type != 'boolean'
                    ) THEN
                        ALTER TABLE auth_user 
                        ALTER COLUMN is_active TYPE boolean 
                        USING CASE 
                            WHEN is_active::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
                            WHEN is_active::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
                            ELSE false
                        END;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE auth_user 
                ALTER COLUMN is_active TYPE integer USING CASE WHEN is_active THEN 1 ELSE 0 END;
            """
        ),
        migrations.RunSQL(
            # Convert is_superuser from bit varying/integer to boolean
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'public'
                        AND table_name = 'auth_user' 
                        AND column_name = 'is_superuser'
                        AND data_type != 'boolean'
                    ) THEN
                        ALTER TABLE auth_user 
                        ALTER COLUMN is_superuser TYPE boolean 
                        USING CASE 
                            WHEN is_superuser::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
                            WHEN is_superuser::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
                            ELSE false
                        END;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE auth_user 
                ALTER COLUMN is_superuser TYPE integer USING CASE WHEN is_superuser THEN 1 ELSE 0 END;
            """
        ),
    ]
