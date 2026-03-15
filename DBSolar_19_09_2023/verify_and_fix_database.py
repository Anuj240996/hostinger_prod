#!/usr/bin/env python
"""
Script to verify and fix the customer_solarpump and customer_controller id column issues.
Run this on your server to ensure the database is properly configured.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection

def fix_table_id_column(cursor, table_name, sequence_name, pkey_name):
    """Helper function to fix id column for a given table"""
    print(f"\n{'=' * 60}")
    print(f"Verifying {table_name} table structure...")
    print("=" * 60)
    
    # Check current state
    cursor.execute(f"""
        SELECT 
            column_name, 
            column_default, 
            is_nullable,
            data_type
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        AND column_name = 'id';
    """)
    
    result = cursor.fetchone()
    if result:
        col_name, col_default, is_nullable, data_type = result
        print(f"\nCurrent state:")
        print(f"  Column: {col_name}")
        print(f"  Type: {data_type}")
        print(f"  Default: {col_default}")
        print(f"  Nullable: {is_nullable}")
        
        # Check if fix is needed
        needs_fix = False
        if col_default is None or 'nextval' not in str(col_default):
            print("\n⚠ WARNING: Default value is not set correctly!")
            needs_fix = True
        if is_nullable == 'YES':
            print("\n⚠ WARNING: Column is nullable!")
            needs_fix = True
        
        if needs_fix:
            print("\n" + "=" * 60)
            print(f"Applying fix to {table_name}...")
            print("=" * 60)
            
            # Step 1: Drop primary key if exists
            print("\nStep 1: Dropping primary key constraint...")
            cursor.execute(f"""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = '{pkey_name}'
                    ) THEN
                        ALTER TABLE {table_name} DROP CONSTRAINT {pkey_name};
                    END IF;
                END $$;
            """)
            print("  ✓ Done")
            
            # Step 2: Drop and recreate sequence
            print("\nStep 2: Recreating sequence...")
            cursor.execute(f"DROP SEQUENCE IF EXISTS {sequence_name} CASCADE;")
            cursor.execute(f"CREATE SEQUENCE {sequence_name};")
            print("  ✓ Done")
            
            # Step 3: Update NULL values
            print("\nStep 3: Updating NULL id values...")
            cursor.execute(f"""
                UPDATE {table_name} 
                SET id = nextval('{sequence_name}') 
                WHERE id IS NULL;
            """)
            updated = cursor.rowcount
            print(f"  ✓ Updated {updated} rows")
            
            # Step 4: Set sequence value
            print("\nStep 4: Setting sequence value...")
            cursor.execute(f"""
                SELECT setval('{sequence_name}', 
                    COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1, false);
            """)
            print("  ✓ Done")
            
            # Step 5: Set NOT NULL
            print("\nStep 5: Setting NOT NULL constraint...")
            cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET NOT NULL;")
            print("  ✓ Done")
            
            # Step 6: Set DEFAULT
            print("\nStep 6: Setting DEFAULT value...")
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ALTER COLUMN id SET DEFAULT nextval('{sequence_name}');
            """)
            print("  ✓ Done")
            
            # Step 7: Add primary key
            print("\nStep 7: Adding primary key constraint...")
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {pkey_name} PRIMARY KEY (id);
            """)
            print("  ✓ Done")
            
            # Step 8: Set sequence ownership
            print("\nStep 8: Setting sequence ownership...")
            cursor.execute(f"ALTER SEQUENCE {sequence_name} OWNED BY {table_name}.id;")
            print("  ✓ Done")
            
            # Verify fix
            print("\n" + "=" * 60)
            print("Verifying fix...")
            print("=" * 60)
            cursor.execute(f"""
                SELECT 
                    column_name, 
                    column_default, 
                    is_nullable,
                    data_type
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'id';
            """)
            result = cursor.fetchone()
            if result:
                col_name, col_default, is_nullable, data_type = result
                print(f"\nNew state:")
                print(f"  Column: {col_name}")
                print(f"  Type: {data_type}")
                print(f"  Default: {col_default}")
                print(f"  Nullable: {is_nullable}")
                
                if 'nextval' in str(col_default) and is_nullable == 'NO':
                    print("\n" + "=" * 60)
                    print(f"✓ SUCCESS! {table_name} is now properly configured.")
                    print("=" * 60)
                    return True
                else:
                    print("\n" + "=" * 60)
                    print(f"⚠ WARNING: Fix for {table_name} may not have worked completely.")
                    print("=" * 60)
                    return False
        else:
            print("\n" + "=" * 60)
            print(f"✓ {table_name} is already properly configured!")
            print("=" * 60)
            return True
    else:
        print(f"\n⚠ ERROR: id column not found in {table_name} table!")
        print("You may need to run migrations first.")
        return False

def verify_and_fix():
    with connection.cursor() as cursor:
        # Fix customer_solarpump table
        fix_table_id_column(
            cursor, 
            'customer_solarpump', 
            'customer_solarpump_id_seq', 
            'customer_solarpump_pkey'
        )
        
        # Fix customer_controller table
        fix_table_id_column(
            cursor, 
            'customer_controller', 
            'customer_controller_id_seq', 
            'customer_controller_pkey'
        )
        
        # Mark migration as applied
        print("\nMarking migration 0028 as applied...")
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('customer', '0028_fix_solarpump_controller_id', NOW())
            ON CONFLICT DO NOTHING;
        """)
        print("  ✓ Done")
        
        print("\n" + "=" * 60)
        print("All done! You can now try creating solar pump and controller entries.")
        print("=" * 60)

if __name__ == '__main__':
    verify_and_fix()

