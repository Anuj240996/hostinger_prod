# Migration: Ensure firereport date columns are TIMESTAMP (datetime) in PostgreSQL
# so that date filtering works correctly. Converts any TEXT/VARCHAR to TIMESTAMP WITH TIME ZONE.
# Applies to: firereport_firereport (postingdate, assignedtime, updationdate, progress_date, working_date, complete_date)
# and firereport_firetequesthistory (postingdate).

from django.db import migrations, connection


def get_column_data_type(table_name, column_name):
    """Return the PostgreSQL data type (e.g. 'timestamp with time zone', 'text')."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND column_name = %s
        """, [table_name, column_name])
        row = cursor.fetchone()
    return (row[0], row[1]) if row else (None, None)


def _convert_column_to_timestamptz(cursor, table_name, col):
    """Convert a single column to timestamp with time zone if it is text/varchar."""
    # Use case-insensitive lookup for column name
    cursor.execute("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND LOWER(column_name) = LOWER(%s)
    """, [table_name, col])
    
    row = cursor.fetchone()
    if not row:
        print(f"Warning: Column '{col}' not found in {table_name}")
        return
    
    actual_col_name, data_type, udt_name = row
    
    # Check if already timestamp type
    if udt_name in ('timestamptz', 'timestamp') or data_type == 'timestamp with time zone':
        print(f"Column {table_name}.{actual_col_name} is already timestamp with time zone. Skipping.")
        return
    
    # Check if it's a text type that needs conversion
    if data_type not in ('text', 'character varying', 'character') and udt_name not in ('varchar', 'text', 'bpchar'):
        print(f"Warning: Column {table_name}.{actual_col_name} has type {data_type} ({udt_name}), not text. Skipping conversion.")
        return
    
    print(f"Converting {table_name}.{actual_col_name} from {data_type} to timestamp with time zone...")
    
    try:
        # Use quoted column name to handle case sensitivity
        cursor.execute(f"""
            ALTER TABLE {table_name}
            ALTER COLUMN "{actual_col_name}"
            TYPE timestamp with time zone
            USING (
                CASE
                    WHEN "{actual_col_name}" IS NULL OR trim("{actual_col_name}"::text) = '' THEN NULL
                    ELSE ("{actual_col_name}"::text)::timestamp with time zone
                END
            )
        """)
        print(f"Successfully converted {table_name}.{actual_col_name} to timestamp with time zone")
    except Exception as e:
        print(f"Error converting {table_name}.{actual_col_name} to timestamptz: {e}")
        import traceback
        print(traceback.format_exc())


def ensure_date_columns_datetime(apps, schema_editor):
    """
    In PostgreSQL, ensure date columns are timestamp with time zone (not text):
    - firereport_firereport: postingdate, assignedtime, updationdate, progress_date, working_date, complete_date
    - firereport_firetequesthistory: postingdate
    """
    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        # firereport_firereport
        table1 = 'firereport_firereport'
        for col in ['postingdate', 'assignedtime', 'updationdate', 'progress_date', 'working_date', 'complete_date']:
            _convert_column_to_timestamptz(cursor, table1, col)

        # firereport_firetequesthistory (same date format / datetime criteria)
        table2 = 'firereport_firetequesthistory'
        _convert_column_to_timestamptz(cursor, table2, 'postingdate')


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('firereport', '0015_alter_firetequesthistory_id'),
    ]

    operations = [
        migrations.RunPython(ensure_date_columns_datetime, noop_reverse),
    ]
