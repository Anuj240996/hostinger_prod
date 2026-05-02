"""
PostgreSQL: FinalSale.return_bill may still be BIT VARYING from legacy DB;
Django BooleanField sends boolean on INSERT → ProgrammingError.
Convert to boolean (same pattern as 0005).
"""

from django.db import migrations


def _udt_name(cursor, table: str, column: str):
    cursor.execute(
        """
        SELECT udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name = %s
        """,
        [table, column],
    )
    row = cursor.fetchone()
    return row[0] if row else None


def _table_exists(cursor, table: str) -> bool:
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        )
        """,
        [table],
    )
    return bool(cursor.fetchone()[0])


def _alter_bit_column_to_boolean(cursor, table: str, column: str, *, nullable: bool):
    if not _table_exists(cursor, table):
        return
    udt = _udt_name(cursor, table, column)
    if udt not in ("varbit", "bit"):
        return

    if nullable:
        using = f"""
            CASE
                WHEN {column} IS NULL THEN NULL
                WHEN bit_length({column}) = 0 THEN FALSE
                ELSE get_bit({column}, 0) = 1
            END
        """
    else:
        using = f"""
            CASE
                WHEN {column} IS NULL THEN FALSE
                WHEN bit_length({column}) = 0 THEN FALSE
                ELSE get_bit({column}, 0) = 1
            END
        """
    cursor.execute(
        f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE boolean USING ({using});'
    )


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        _alter_bit_column_to_boolean(
            cursor,
            "transactions_finalsale",
            "return_bill",
            nullable=False,
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0007_fix_detail_and_item_id_sequences"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
