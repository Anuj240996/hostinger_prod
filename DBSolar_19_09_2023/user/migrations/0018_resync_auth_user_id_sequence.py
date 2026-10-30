from django.db import migrations


RESYNC_SQL = """
DO $$
DECLARE
    seq_name text;
    max_id bigint;
BEGIN
    SELECT pg_get_serial_sequence('auth_user', 'id') INTO seq_name;
    IF seq_name IS NOT NULL THEN
        SELECT COALESCE(MAX(id), 0) INTO max_id FROM auth_user;
        IF max_id > 0 THEN
            PERFORM setval(seq_name, max_id, true);
        ELSE
            PERFORM setval(seq_name, 1, false);
        END IF;
    END IF;

    SELECT pg_get_serial_sequence('user_profile', 'id') INTO seq_name;
    IF seq_name IS NOT NULL THEN
        SELECT COALESCE(MAX(id), 0) INTO max_id FROM user_profile;
        IF max_id > 0 THEN
            PERFORM setval(seq_name, max_id, true);
        ELSE
            PERFORM setval(seq_name, 1, false);
        END IF;
    END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0017_alter_profile_customer_alter_profile_image"),
    ]

    operations = [
        migrations.RunSQL(sql=RESYNC_SQL, reverse_sql=migrations.RunSQL.noop),
    ]
