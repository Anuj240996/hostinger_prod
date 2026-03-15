# Migration: Fix firereport_firetequesthistory.postingdate to be TIMESTAMP (datetime) in PostgreSQL
# Ensures the column is timestamp with time zone, not text, so date filtering works correctly.

from django.db import migrations, connection


def fix_firetequesthistory_postingdate_datetime(apps, schema_editor):
    """
    Convert firereport_firetequesthistory.postingdate from TEXT to TIMESTAMP WITH TIME ZONE.
    Handles case-insensitive column name lookup.
    """
    if connection.vendor != 'postgresql':
        return

    table_name = 'firereport_firetequesthistory'
    
    with connection.cursor() as cursor:
        # First, find the actual column name (case-insensitive)
        cursor.execute("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND LOWER(column_name) = 'postingdate'
        """, [table_name])
        
        row = cursor.fetchone()
        if not row:
            print(f"Warning: Column 'postingdate' not found in {table_name}")
            return
        
        actual_col_name, data_type, udt_name = row
        print(f"Found column '{actual_col_name}' in {table_name}: data_type={data_type}, udt_name={udt_name}")
        
        # Check if already timestamp type
        if udt_name in ('timestamptz', 'timestamp') or data_type == 'timestamp with time zone':
            print(f"Column '{actual_col_name}' is already timestamp with time zone. No conversion needed.")
            return
        
        # Check if it's a text type that needs conversion
        if data_type not in ('text', 'character varying', 'character') and udt_name not in ('varchar', 'text', 'bpchar'):
            print(f"Warning: Column '{actual_col_name}' has unexpected type: {data_type} ({udt_name}). Skipping conversion.")
            return
        
        print(f"Converting column '{actual_col_name}' from {data_type} to timestamp with time zone...")
        
        # Check a sample value to understand the format
        cursor.execute(f"""
            SELECT "{actual_col_name}" 
            FROM {table_name} 
            WHERE "{actual_col_name}" IS NOT NULL 
            LIMIT 3
        """)
        samples = cursor.fetchall()
        if samples:
            for idx, sample in enumerate(samples):
                print(f"Sample {idx+1}: {repr(sample[0])}")
        
        # Strategy: Use a temporary column, convert data, then swap
        temp_col = f"{actual_col_name}_temp_timestamptz"
        
        try:
            # Step 1: Add temporary timestamp column
            print(f"Adding temporary column '{temp_col}'...")
            cursor.execute(f"""
                ALTER TABLE {table_name}
                ADD COLUMN "{temp_col}" timestamp with time zone NULL
            """)
            
            # Step 2: Copy and convert data from text to timestamp
            print(f"Converting data from '{actual_col_name}' to '{temp_col}'...")
            cursor.execute(f"""
                UPDATE {table_name}
                SET "{temp_col}" = CASE
                    WHEN "{actual_col_name}" IS NULL OR trim("{actual_col_name}"::text) = '' THEN NULL
                    -- Try direct cast first (handles ISO format with timezone)
                    ELSE 
                        CASE
                            -- If it has timezone info, cast directly
                            WHEN trim("{actual_col_name}"::text) ~ '[+-][0-9]{2}:?[0-9]{0,2}$' THEN
                                trim("{actual_col_name}"::text)::timestamp with time zone
                            -- Otherwise, parse as timestamp without timezone and assume UTC
                            ELSE
                                (trim("{actual_col_name}"::text)::timestamp without time zone) AT TIME ZONE 'UTC'
                        END
                END
            """)
            
            # Step 3: Drop old column
            print(f"Dropping old column '{actual_col_name}'...")
            cursor.execute(f"""
                ALTER TABLE {table_name}
                DROP COLUMN "{actual_col_name}"
            """)
            
            # Step 4: Rename temporary column to original name
            print(f"Renaming '{temp_col}' to '{actual_col_name}'...")
            cursor.execute(f"""
                ALTER TABLE {table_name}
                RENAME COLUMN "{temp_col}" TO "{actual_col_name}"
            """)
            
            print(f"Successfully converted '{actual_col_name}' to timestamp with time zone")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error during conversion: {error_msg}")
            
            # Cleanup: drop temp column if it exists
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    DROP COLUMN IF EXISTS "{temp_col}"
                """)
            except:
                pass
            
            # Try simpler direct conversion as fallback
            try:
                print("Trying direct ALTER COLUMN conversion...")
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    ALTER COLUMN "{actual_col_name}"
                    TYPE timestamp with time zone
                    USING NULLIF(trim("{actual_col_name}"::text), '')::timestamp with time zone
                """)
                print(f"Successfully converted '{actual_col_name}' using direct conversion")
            except Exception as e2:
                print(f"Direct conversion also failed: {str(e2)}")
                raise


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('firereport', '0016_ensure_firereport_date_columns_datetime'),
    ]

    operations = [
        migrations.RunPython(fix_firetequesthistory_postingdate_datetime, noop_reverse),
    ]
