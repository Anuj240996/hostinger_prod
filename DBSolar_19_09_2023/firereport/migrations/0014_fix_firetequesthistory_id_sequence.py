# Generated migration to fix Firetequesthistory id sequence

from django.db import migrations, connection
from django.db.backends.postgresql.schema import DatabaseSchemaEditor


def fix_firetequesthistory_id_sequence(apps, schema_editor):
    """Fix the id sequence for firereport_firetequesthistory table"""
    db_alias = schema_editor.connection.alias
    with connection.cursor() as cursor:
        # Get the current maximum id from the table
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM firereport_firetequesthistory")
        max_id = cursor.fetchone()[0]
        
        # Find the actual sequence name used by the id column (with schema)
        cursor.execute("""
            SELECT pg_get_serial_sequence('firereport_firetequesthistory', 'id')
        """)
        seq_result = cursor.fetchone()
        sequence_full_name = seq_result[0] if seq_result and seq_result[0] else None
        
        if sequence_full_name:
            # Use the full sequence name (includes schema)
            # Sync the sequence value
            next_val = max_id + 1 if max_id > 0 else 1
            try:
                # Use the full sequence name with proper quoting
                cursor.execute(f"SELECT setval(%s, %s, false)", [sequence_full_name, next_val])
            except Exception as e:
                # If that fails, try without schema qualification
                sequence_name = sequence_full_name.split('.')[-1] if '.' in sequence_full_name else sequence_full_name
                try:
                    cursor.execute(f"SELECT setval('{sequence_name}', {next_val}, false)")
                except Exception as e2:
                    print(f"Warning: Could not sync sequence: {e2}")
        else:
            # Try to find any sequence that might be related
            cursor.execute("""
                SELECT sequencename 
                FROM pg_sequences 
                WHERE sequencename LIKE '%firetequesthistory%'
            """)
            seq_names = cursor.fetchall()
            if seq_names:
                sequence_name = seq_names[0][0]
                next_val = max_id + 1 if max_id > 0 else 1
                try:
                    cursor.execute(f"SELECT setval('{sequence_name}', {next_val}, false)")
                except Exception as e:
                    print(f"Warning: Could not sync sequence {sequence_name}: {e}")


def reverse_fix_sequence(apps, schema_editor):
    """Reverse operation - no-op"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('firereport', '0013_alter_firetequesthistory_assignby'),
    ]

    operations = [
        migrations.RunPython(fix_firetequesthistory_id_sequence, reverse_fix_sequence),
    ]
