"""
PostgreSQL: dashboard_staff_notification.id serial repair after legacy import.
Skipped when id is already a PostgreSQL IDENTITY column (fresh Django 5.1 DB).
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        fix_pg_serial_column(
            cursor,
            schema_editor,
            "dashboard_staff_notification",
            "id",
            "dashboard_staff_notification_id_seq",
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_fix_staff_notification_boolean_fields"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
