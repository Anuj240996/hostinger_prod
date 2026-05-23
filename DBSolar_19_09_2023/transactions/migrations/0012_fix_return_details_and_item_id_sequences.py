"""
PostgreSQL: BigAutoField ``id`` without DEFAULT nextval(...) on return-sale tables.
Fixes NULL id on INSERT (same pattern as 0007 / 0010).
Also fixes transactions_returnsaleitem proactively (same issue after submit).
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("transactions_returnbilldetails", "id", "transactions_returnbilldetails_id_seq"),
        ("transactions_returnsaleitem", "id", "transactions_returnsaleitem_id_seq"),
    ]

    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0011_fix_returnsale_billno_sequence"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
