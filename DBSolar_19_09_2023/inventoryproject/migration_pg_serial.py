"""
Helpers for PostgreSQL serial/sequence repair migrations (MySQL -> Postgres imports).

On fresh Django 5.1+ databases, BigAutoField columns use IDENTITY; do not run
legacy nextval() ALTER DEFAULT (PostgreSQL rejects it).
"""


def table_owner_rolname(cursor, table: str):
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


def is_pg_identity_column(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT a.attidentity
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class c ON c.oid = a.attrelid
        JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname = %s
          AND a.attname = %s
          AND a.attnum > 0
          AND NOT a.attisdropped
        """,
        [table, column],
    )
    row = cursor.fetchone()
    return bool(row and row[0] in ("a", "d"))


def fix_pg_serial_column(cursor, schema_editor, table: str, column: str, default_seq: str):
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

    if is_pg_identity_column(cursor, table, column):
        return

    owner = table_owner_rolname(cursor, table)

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
        if not is_pg_identity_column(cursor, table, column):
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
