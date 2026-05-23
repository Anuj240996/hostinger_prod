"""PostgreSQL: repair solarpump/controller id serial defaults after MySQL import."""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        fix_pg_serial_column(
            cursor,
            schema_editor,
            "customer_solarpump",
            "id",
            "customer_solarpump_id_seq",
        )
        fix_pg_serial_column(
            cursor,
            schema_editor,
            "customer_controller",
            "id",
            "customer_controller_id_seq",
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("customer", "0114_fix_inspectiondetail_id_sequence"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
