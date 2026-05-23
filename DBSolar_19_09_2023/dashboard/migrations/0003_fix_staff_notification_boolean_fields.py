from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_fix_auth_user_boolean_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = 'dashboard_staff_notification'
                          AND column_name = 'read'
                          AND data_type != 'boolean'
                    ) THEN
                        ALTER TABLE dashboard_staff_notification
                        ALTER COLUMN "read" TYPE boolean
                        USING CASE
                            WHEN "read"::text IN ('1', 'true', 't', 'TRUE', 'T', 'True', 'B''1''') THEN true
                            WHEN "read"::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '', 'B''0''') THEN false
                            ELSE false
                        END;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE dashboard_staff_notification
                ALTER COLUMN "read" TYPE bit varying
                USING CASE WHEN "read" THEN B'1' ELSE B'0' END;
            """,
        ),
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = 'dashboard_staff_notification'
                          AND column_name = 'is_current'
                          AND data_type != 'boolean'
                    ) THEN
                        ALTER TABLE dashboard_staff_notification
                        ALTER COLUMN is_current TYPE boolean
                        USING CASE
                            WHEN is_current::text IN ('1', 'true', 't', 'TRUE', 'T', 'True', 'B''1''') THEN true
                            WHEN is_current::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '', 'B''0''') THEN false
                            ELSE true
                        END;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE dashboard_staff_notification
                ALTER COLUMN is_current TYPE bit varying
                USING CASE WHEN is_current THEN B'1' ELSE B'0' END;
            """,
        ),
    ]
