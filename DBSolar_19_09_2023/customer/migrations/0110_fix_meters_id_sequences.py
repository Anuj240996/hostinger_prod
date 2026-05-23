"""
PostgreSQL: repair serial defaults on meter tables after MySQL-style migration.
Skipped on fresh DBs where id columns are PostgreSQL IDENTITY (Django 5.1+).
"""

from django.db import migrations

from inventoryproject.migration_pg_serial import fix_pg_serial_column


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("customer_meters", "id", "customer_meters_id_seq"),
        ("customer_generationmeter", "id", "customer_generationmeter_id_seq"),
        ("customer_generationct", "id", "customer_generationct_id_seq"),
    ]

    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("customer", "0108_alter_customer_cust_id"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
