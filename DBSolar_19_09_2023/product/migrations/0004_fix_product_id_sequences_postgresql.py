"""
PostgreSQL: product_* .id without DEFAULT nextval(...) causes NULL id on INSERT
after MySQL-style migration. Skipped when id is already PostgreSQL IDENTITY (fresh DB).
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

PRODUCT_ID_TABLES = (
    ("product_category", "product_category_id_seq"),
    ("product_subcategory", "product_subcategory_id_seq"),
    ("product_product", "product_product_id_seq"),
    ("product_unit", "product_unit_id_seq"),
    ("product_brand", "product_brand_id_seq"),
    ("product_supplier", "product_supplier_id_seq"),
)


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
