from django.db import migrations


RESYNC_SQL = """
DO $$
DECLARE
    seq_name text;
    max_id bigint;
BEGIN
    SELECT pg_get_serial_sequence('firereport_firetequesthistory', 'id') INTO seq_name;
    IF seq_name IS NULL THEN
        RETURN;
    END IF;
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM firereport_firetequesthistory;
    IF max_id > 0 THEN
        PERFORM setval(seq_name, max_id, true);
    ELSE
        PERFORM setval(seq_name, 1, false);
    END IF;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("firereport", "0021_fix_firetequesthistory_column_case"),
    ]

    operations = [
        migrations.RunSQL(sql=RESYNC_SQL, reverse_sql=migrations.RunSQL.noop),
    ]
