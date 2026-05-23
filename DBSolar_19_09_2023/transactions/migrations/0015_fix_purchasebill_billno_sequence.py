"""PostgreSQL: PurchaseBill.billno sequence repair; skip on fresh IDENTITY columns."""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        fix_pg_serial_column(
            cursor,
            schema_editor,
            "transactions_purchasebill",
            "billno",
            "transactions_purchasebill_billno_seq",
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0014_fix_supplier_vendor_id_sequences"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
