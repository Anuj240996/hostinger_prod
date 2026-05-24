# Legacy PostgreSQL (from MySQL) keeps mixed-case FK columns Cust_id_id / Vend_id_id.
# Migration 0002 incorrectly set Django state to lowercase cust_id_id / vend_id_id.

import django.db.models.deletion
from django.db import migrations, models


def _column_exists(cursor, table, column):
    cursor.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        [table, column],
    )
    return cursor.fetchone() is not None


def align_salebill_fk_columns(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        renames = (
            ("cust_id_id", "Cust_id_id"),
            ("vend_id_id", "Vend_id_id"),
        )
        for old_name, new_name in renames:
            if _column_exists(cursor, "transactions_salebill", old_name) and not _column_exists(
                cursor, "transactions_salebill", new_name
            ):
                cursor.execute(
                    f'ALTER TABLE transactions_salebill RENAME COLUMN "{old_name}" TO "{new_name}"'
                )


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0016_fix_purchase_details_and_item_id_sequences"),
    ]

    operations = [
        migrations.RunPython(align_salebill_fk_columns, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="salebill",
                    name="Cust_id",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="Cust_id_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="salescustomer",
                        to="customer.customer",
                    ),
                ),
                migrations.AlterField(
                    model_name="salebill",
                    name="Vend_id",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="Vend_id_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="salesvendor",
                        to="transactions.vendor",
                    ),
                ),
            ],
        ),
    ]
