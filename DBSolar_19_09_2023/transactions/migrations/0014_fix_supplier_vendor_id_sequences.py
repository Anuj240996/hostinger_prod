"""
PostgreSQL: transactions_supplier.id (and vendor) missing DEFAULT / out-of-sync sequence
causes NULL id on INSERT. Same pattern as 0007 / 0012.
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("transactions_supplier", "id", "transactions_supplier_id_seq"),
        ("transactions_vendor", "id", "transactions_vendor_id_seq"),
    ]

    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0013_fix_supplier_vendor_status_bit_to_boolean"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
