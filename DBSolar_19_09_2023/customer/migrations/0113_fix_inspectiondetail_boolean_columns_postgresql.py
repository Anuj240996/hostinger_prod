"""
PostgreSQL: customer_inspectiondetail *_completed / info_correct columns may be
bit varying (varbit) while Django BooleanField sends boolean — same fix as 0111.

Safe to re-run: only alters columns that are still udt_name = 'varbit'.
"""

from django.db import migrations


INSPECTION_BOOLEAN_COLUMNS = (
    "solar_module_completed",
    "inverter_completed",
    "net_meter_completed",
    "ct_completed",
    "generation_meters_completed",
    "gen_ct_meters_completed",
    "ac_panel_cabling_completed",
    "dc_panel_cabling_completed",
    "fabrication_completed",
    "walkway_completed",
    "pipeline_completed",
    "ropeway_completed",
    "rolling_completed",
    "info_correct",
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


def alter_inspection_varbit_to_boolean(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    table = "customer_inspectiondetail"
    with connection.cursor() as cursor:
        for col in INSPECTION_BOOLEAN_COLUMNS:
            if not _is_varbit_column(cursor, table, col):
                continue
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
        ("customer", "0112_fix_mseb_id_sequence"),
    ]

    operations = [
        migrations.RunPython(alter_inspection_varbit_to_boolean, noop_reverse),
    ]
