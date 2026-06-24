"""
PostgreSQL: inventory_favoritelist.id / inventory_favoriteliststock.id
missing DEFAULT nextval → NULL on INSERT. Same pattern as transactions.0014.
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


def _fix_pg_serial_column(cursor, schema_editor, table: str, column: str, default_seq: str):
    qn = schema_editor.connection.ops.quote_name

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
    max_id = cursor.fetchone()[0]

    if max_id == 0:
        cursor.execute(
            "SELECT setval(%s::regclass, 1, false);",
            [seq_name],
        )
    else:
        cursor.execute(
            "SELECT setval(%s::regclass, %s);",
            [seq_name, max_id],
        )


def forwards(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    targets = [
        ("inventory_favoritelist", "id", "inventory_favoritelist_id_seq"),
        ("inventory_favoriteliststock", "id", "inventory_favoriteliststock_id_seq"),
    ]
    with schema_editor.connection.cursor() as cursor:
        for table, column, default_seq in targets:
            _fix_pg_serial_column(cursor, schema_editor, table, column, default_seq)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0003_alter_stock_bit_columns_to_boolean"),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
