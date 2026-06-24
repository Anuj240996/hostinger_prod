"""
PostgreSQL: ReturnSale.billno AutoField may have no sequence DEFAULT (MySQL migration).
Inserts then send NULL for billno → NOT NULL violation. Same pattern as 0006 / 0009.
"""

from django.db import migrations


def _table_owner_rolname(cursor, table: str):
    cursor.execute(
        """
        SELECT r.rolname
        FROM pg_catalog.pg_class c
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_catalog.pg_roles r ON r.oid = c.relowner
        WHERE n.nspname = 'public'
          AND c.relname = %s
          AND c.relkind = 'r'
        """,
        [table],
    )
    row = cursor.fetchone()
    return row[0] if row else None


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    table = "transactions_returnsale"
    column = "billno"
    default_seq = "transactions_returnsale_billno_seq"

    qn = schema_editor.connection.ops.quote_name

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
            )
            """,
            [table],
        )
        if not cursor.fetchone()[0]:
            return

        owner = _table_owner_rolname(cursor, table)

        cursor.execute(
            "SELECT pg_get_serial_sequence(%s, %s);",
            [table, column],
        )
        row = cursor.fetchone()
        seq_name = row[0] if row else None

        if not seq_name:
            cursor.execute(f'CREATE SEQUENCE IF NOT EXISTS "{default_seq}";')
            if owner:
                cursor.execute(
                    f"ALTER SEQUENCE {qn(default_seq)} OWNER TO {qn(owner)};"
                )
            cursor.execute(
                f"""
                ALTER TABLE "{table}"
                ALTER COLUMN "{column}"
                SET DEFAULT nextval('"{default_seq}"'::regclass);
                """
            )
            cursor.execute(
                "SELECT pg_get_serial_sequence(%s, %s);",
                [table, column],
            )
            seq_name = cursor.fetchone()[0]
        elif owner and seq_name:
            cursor.execute(
                f"ALTER SEQUENCE {seq_name} OWNER TO {qn(owner)};"
            )

        cursor.execute(
            """
            SELECT column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
            """,
            [table, column],
        )
        col_default = (cursor.fetchone() or [None])[0] or ""
        if seq_name and "nextval" not in col_default.lower():
            cursor.execute(
                f"""
                ALTER TABLE "{table}"
                ALTER COLUMN "{column}"
                SET DEFAULT nextval(%s::regclass);
                """,
                [seq_name],
            )

        if not seq_name:
            return

        cursor.execute(f'SELECT COALESCE(MAX("{column}"), 0) FROM "{table}";')
        max_billno = cursor.fetchone()[0]

        if max_billno == 0:
            cursor.execute(
                "SELECT setval(%s::regclass, 1, false);",
                [seq_name],
            )
        else:
            cursor.execute(
                "SELECT setval(%s::regclass, %s);",
                [seq_name, max_billno],
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0010_fix_finalsaleitem_id_sequence"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
