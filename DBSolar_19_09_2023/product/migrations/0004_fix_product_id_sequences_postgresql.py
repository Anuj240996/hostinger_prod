"""
PostgreSQL: product_* .id without DEFAULT nextval(...) causes NULL id on INSERT
after MySQL-style migration. Same pattern as customer.0112_fix_mseb_id_sequence.
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        for table, seq in PRODUCT_ID_TABLES:
            fix_pg_serial_column(cursor, schema_editor, table, "id", seq)



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0003_fix_status_boolean_columns_postgresql"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
