"""
PostgreSQL: detect_barcodes ids can lose DEFAULT nextval(...) after legacy migrations,
causing NULL id on INSERT for BarcodeImage / InverterImage.
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        fix_pg_serial_column(
            cursor, schema_editor, "detect_barcodes_barcodeimage", "id", "detect_barcodes_barcodeimage_id_seq"
        )
        fix_pg_serial_column(
            cursor, schema_editor, "detect_barcodes_inverterimage", "id", "detect_barcodes_inverterimage_id_seq"
        )



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("detect_barcodes", "0003_alter_barcodeimage_assignby_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]

