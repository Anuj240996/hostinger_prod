"""
PostgreSQL: inventory_favoritelist.id / inventory_favoriteliststock.id
missing DEFAULT nextval → NULL on INSERT. Same pattern as transactions.0014.
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column

def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("inventory_favoritelist", "id", "inventory_favoritelist_id_seq"),
        ("inventory_favoriteliststock", "id", "inventory_favoriteliststock_id_seq"),
    ]
    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)



def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0003_alter_stock_bit_columns_to_boolean"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
