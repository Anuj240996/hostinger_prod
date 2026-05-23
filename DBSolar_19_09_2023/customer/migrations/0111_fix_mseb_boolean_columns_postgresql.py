"""
PostgreSQL: customer_mseb step columns were created as bit varying (varbit).
Django BooleanField sends boolean — fix: ALTER COLUMN ... TYPE boolean USING (...).

Safe to re-run: only alters columns that are still udt_name = 'varbit'.
"""

from django.db import migrations


MSEB_BOOLEAN_COLUMNS = (
    "load_extension",
    "flisibility",
    "quotation",
    "sent_to_bill",
    "net_meter",
    "flexibility",
    "approval",
    "meter_testing",
    "agreement",
    "release",
    "installation_date",
)


def _is_varbit_column(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT c.udt_name
        FROM information_schema.columns c
        WHERE c.table_schema = current_schema()
          AND c.table_name = %s
          AND c.column_name = %s
        """,
        [table_name, column_name],
    )
    row = cursor.fetchone()
    return bool(row and row[0] == "varbit")


def alter_mseb_varbit_to_boolean(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    table = "customer_mseb"
    with connection.cursor() as cursor:
        for col in MSEB_BOOLEAN_COLUMNS:
            if not _is_varbit_column(cursor, table, col):
                continue
            # varbit: treat NULL / empty as false; first bit 1 as true
            cursor.execute(
                f"""
                ALTER TABLE {table}
                ALTER COLUMN "{col}" TYPE boolean USING (
                    CASE
                        WHEN "{col}" IS NULL OR bit_length("{col}") = 0 THEN false
                        ELSE get_bit("{col}", 0) = 1
                    END
                );
                """
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("customer", "0110_fix_meters_id_sequences"),
    ]

    operations = [
        migrations.RunPython(alter_mseb_varbit_to_boolean, noop_reverse),
    ]
