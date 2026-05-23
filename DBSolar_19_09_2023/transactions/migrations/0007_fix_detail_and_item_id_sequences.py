"""
PostgreSQL: BigAutoField ``id`` columns without DEFAULT nextval(...) cause NULL id
on INSERT (common after MySQL migration). Fix sequence + DEFAULT + setval per table.
Same pattern as 0006 (no OWNED BY; sequence OWNER aligned to table).
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("transactions_salebilldetails", "id", "transactions_salebilldetails_id_seq"),
        ("transactions_saleitem", "id", "transactions_saleitem_id_seq"),
    ]

    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0006_fix_salebill_billno_sequence"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
