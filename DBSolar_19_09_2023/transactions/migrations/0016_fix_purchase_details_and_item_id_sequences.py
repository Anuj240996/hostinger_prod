"""
PostgreSQL: BigAutoField ``id`` on purchase-related tables without DEFAULT nextval(...)
causes NULL id on INSERT (same root cause as 0007 / 0015).

Fixes: PurchaseBillDetails, PurchaseItem, PurchaseSerial.
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("transactions_purchasebilldetails", "id", "transactions_purchasebilldetails_id_seq"),
        ("transactions_purchaseitem", "id", "transactions_purchaseitem_id_seq"),
        ("transactions_purchaseserial", "id", "transactions_purchaseserial_id_seq"),
    ]

    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0015_fix_purchasebill_billno_sequence"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
