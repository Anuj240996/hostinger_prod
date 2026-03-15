#!/usr/bin/env python
"""
COMPREHENSIVE FIX for all id column issues:
- customer_solarpump
- customer_controller  
- customer_meters
- customer_generationmeter

Run this script to fix all tables at once
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
    print(f"\n{'=' * 70}")
    print(f"FIXING {table_name} id COLUMN")
    print("=" * 70)
    
    try:
        print("\n1. Dropping primary key constraint...")
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            DROP CONSTRAINT IF EXISTS {pkey_name};
        """)
        print("   ✓ Done")
        
        print("\n2. Dropping old sequence...")
        cursor.execute(f"DROP SEQUENCE IF EXISTS {sequence_name} CASCADE;")
        print("   ✓ Done")
        
        print("\n3. Creating new sequence...")
        cursor.execute(f"CREATE SEQUENCE {sequence_name};")
        print("   ✓ Done")
        
        print("\n4. Updating NULL id values...")
        cursor.execute(f"""
            UPDATE {table_name} 
            SET id = nextval('{sequence_name}') 
            WHERE id IS NULL;
        """)
        updated = cursor.rowcount
        print(f"   ✓ Updated {updated} rows")
        
        print("\n5. Setting sequence value...")
        cursor.execute(f"""
            SELECT setval('{sequence_name}', 
                COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1, false);
        """)
        print("   ✓ Done")
        
        print("\n6. Setting NOT NULL constraint...")
        cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET NOT NULL;")
        print("   ✓ Done")
        
        print("\n7. Setting DEFAULT value (THIS IS THE KEY FIX!)...")
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ALTER COLUMN id SET DEFAULT nextval('{sequence_name}');
        """)
        print("   ✓ Done")
        
        print("\n8. Adding primary key constraint...")
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ADD CONSTRAINT {pkey_name} PRIMARY KEY (id);
        """)
        print("   ✓ Done")
        
        print("\n9. Setting sequence ownership...")
        cursor.execute(f"ALTER SEQUENCE {sequence_name} OWNED BY {table_name}.id;")
        print("   ✓ Done")
        
        # Verify
        print("\nVerifying fix...")
        cursor.execute(f"""
            SELECT column_name, column_default, is_nullable, data_type
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name = 'id';
        """)
        result = cursor.fetchone()
        if result:
            col_name, col_default, is_nullable, data_type = result
            if col_default and 'nextval' in str(col_default) and is_nullable == 'NO':
                print(f"   ✓ {table_name} is now properly configured!")
                return True
            else:
                print(f"   ⚠ {table_name} may not be fully fixed")
                return False
        else:
            print(f"   ⚠ Could not verify {table_name}")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR fixing {table_name}: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("FIXING ALL ID COLUMNS")
    print("=" * 70)
    
    tables_to_fix = [
        ('customer_solarpump', 'customer_solarpump_id_seq', 'customer_solarpump_pkey'),
        ('customer_controller', 'customer_controller_id_seq', 'customer_controller_pkey'),
        ('customer_meters', 'customer_meters_id_seq', 'customer_meters_pkey'),
        ('customer_generationmeter', 'customer_generationmeter_id_seq', 'customer_generationmeter_pkey'),
    ]
    
    with connection.cursor() as cursor:
        results = []
        for table_name, sequence_name, pkey_name in tables_to_fix:
            success = fix_table_id_column(cursor, table_name, sequence_name, pkey_name)
            results.append((table_name, success))
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for table_name, success in results:
        status = "✓ FIXED" if success else "✗ FAILED"
        print(f"{status}: {table_name}")
    
    print("\n" + "=" * 70)
    print("IMPORTANT: RESTART your Django server after running this fix!")
    print("=" * 70)

