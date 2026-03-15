#!/usr/bin/env python
"""
IMMEDIATE FIX for customer_meters id column issue
Run this script directly on your server to fix the database
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection

print("=" * 70)
print("FIXING customer_meters id COLUMN")
print("=" * 70)

with connection.cursor() as cursor:
    try:
        print("\n1. Dropping primary key constraint...")
        cursor.execute("""
            ALTER TABLE customer_meters 
            DROP CONSTRAINT IF EXISTS customer_meters_pkey;
        """)
        print("   ✓ Done")
        
        print("\n2. Dropping old sequence...")
        cursor.execute("DROP SEQUENCE IF EXISTS customer_meters_id_seq CASCADE;")
        print("   ✓ Done")
        
        print("\n3. Creating new sequence...")
        cursor.execute("CREATE SEQUENCE customer_meters_id_seq;")
        print("   ✓ Done")
        
        print("\n4. Updating NULL id values...")
        cursor.execute("""
            UPDATE customer_meters 
            SET id = nextval('customer_meters_id_seq') 
            WHERE id IS NULL;
        """)
        updated = cursor.rowcount
        print(f"   ✓ Updated {updated} rows")
        
        print("\n5. Setting sequence value...")
        cursor.execute("""
            SELECT setval('customer_meters_id_seq', 
                COALESCE((SELECT MAX(id) FROM customer_meters), 0) + 1, false);
        """)
        print("   ✓ Done")
        
        print("\n6. Setting NOT NULL constraint...")
        cursor.execute("ALTER TABLE customer_meters ALTER COLUMN id SET NOT NULL;")
        print("   ✓ Done")
        
        print("\n7. Setting DEFAULT value (THIS IS THE KEY FIX!)...")
        cursor.execute("""
            ALTER TABLE customer_meters 
            ALTER COLUMN id SET DEFAULT nextval('customer_meters_id_seq');
        """)
        print("   ✓ Done")
        
        print("\n8. Adding primary key constraint...")
        cursor.execute("""
            ALTER TABLE customer_meters 
            ADD CONSTRAINT customer_meters_pkey PRIMARY KEY (id);
        """)
        print("   ✓ Done")
        
        print("\n9. Setting sequence ownership...")
        cursor.execute("ALTER SEQUENCE customer_meters_id_seq OWNED BY customer_meters.id;")
        print("   ✓ Done")
        
        # Verify
        print("\n" + "=" * 70)
        print("VERIFYING FIX...")
        print("=" * 70)
        cursor.execute("""
            SELECT column_name, column_default, is_nullable, data_type
            FROM information_schema.columns 
            WHERE table_name = 'customer_meters' 
            AND column_name = 'id';
        """)
        result = cursor.fetchone()
        if result:
            col_name, col_default, is_nullable, data_type = result
            print(f"\nColumn: {col_name}")
            print(f"Type: {data_type}")
            print(f"Default: {col_default}")
            print(f"Nullable: {is_nullable}")
            
            if col_default and 'nextval' in str(col_default) and is_nullable == 'NO':
                print("\n" + "=" * 70)
                print("✓ SUCCESS! The id column is now properly configured.")
                print("=" * 70)
                print("\nYou can now try creating meter entries again.")
                print("Make sure to RESTART your Django server after this fix!")
            else:
                print("\n" + "=" * 70)
                print("⚠ WARNING: The fix may not have worked completely.")
                print("=" * 70)
                print(f"Expected: default with 'nextval' and is_nullable='NO'")
                print(f"Got: default={col_default}, is_nullable={is_nullable}")
        else:
            print("\n⚠ ERROR: Could not find id column!")
            
    except Exception as e:
        print("\n" + "=" * 70)
        print("✗ ERROR OCCURRED:")
        print("=" * 70)
        print(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

