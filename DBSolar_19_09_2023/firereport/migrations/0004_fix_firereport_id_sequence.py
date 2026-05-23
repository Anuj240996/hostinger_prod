from __future__ import annotations

from django.db import migrations


def fix_firereport_id_sequence(apps, schema_editor):
    """
    Legacy DB repair:
    Ensure firereport_firereport.id has an auto-increment sequence default.

    Fixes:
      IntegrityError: null value in column "id" ... violates not-null constraint
    """
    conn = schema_editor.connection
    if conn.vendor != "postgresql":
        return

    table = "firereport_firereport"
    seq = "firereport_firereport_id_seq"

    with conn.cursor() as cursor:
        # If default is already set, do nothing.
        cursor.execute(
            """
            SELECT column_default
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = 'id'
            """,
            [table],
        )
        row = cursor.fetchone()
        default = row[0] if row else None
        if default and "nextval" in str(default):
            return

        # Create sequence if missing.
        cursor.execute(f'CREATE SEQUENCE IF NOT EXISTS "{seq}"')

        # Align sequence with current max(id).
        cursor.execute(f'SELECT COALESCE(MAX(id), 0) FROM "{table}"')
        max_id = cursor.fetchone()[0] or 0
        if max_id <= 0:
            cursor.execute(f"SELECT setval(%s, 1, false)", [seq])
        else:
            cursor.execute(f"SELECT setval(%s, %s, true)", [seq, max_id])

        # Set default. (Do NOT run ALTER SEQUENCE ... OWNED BY here; if it fails,
        # PostgreSQL aborts the whole transaction even if we catch the exception.)
        cursor.execute(f'ALTER TABLE "{table}" ALTER COLUMN "id" SET DEFAULT nextval(%s)', [seq])


class Migration(migrations.Migration):
    dependencies = [
        ("firereport", "0003_alter_firereport_message"),
    ]

    operations = [
        migrations.RunPython(fix_firereport_id_sequence, reverse_code=migrations.RunPython.noop),
    ]

