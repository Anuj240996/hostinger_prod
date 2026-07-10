from django.db import migrations


RESYNC_SQL = """
DO $$
DECLARE
    seq_name text;
    max_id bigint;
BEGIN
    SELECT pg_get_serial_sequence('customer_result', 'id') INTO seq_name;
    IF seq_name IS NULL THEN
        RETURN;
    END IF;
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM customer_result;
    IF max_id > 0 THEN
        PERFORM setval(seq_name, max_id, true);
    ELSE
        PERFORM setval(seq_name, 1, false);
    END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("customer", "0121_mobile_app_backend_schema"),
    ]

    operations = [
        migrations.RunSQL(sql=RESYNC_SQL, reverse_sql=migrations.RunSQL.noop),
    ]
