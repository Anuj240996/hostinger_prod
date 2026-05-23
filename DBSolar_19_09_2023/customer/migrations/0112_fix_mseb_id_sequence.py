"""PostgreSQL: repair customer_mseb.id serial default after MySQL import."""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        fix_pg_serial_column(
            cursor,
            schema_editor,
            "customer_mseb",
            "id",
            "customer_mseb_id_seq",
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("customer", "0111_fix_mseb_boolean_columns_postgresql"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
