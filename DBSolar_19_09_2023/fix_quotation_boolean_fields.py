#!/usr/bin/env python
"""
Fix boolean fields in quotation_termsandcondition table.
Converts bit varying columns to boolean type.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection

def fix_quotation_boolean_fields():
    """Convert bit varying to boolean for quotation_termsandcondition table"""
    
    with connection.cursor() as cursor:
        print("=" * 80)
        print("FIXING QUOTATION BOOLEAN FIELDS")
        print("=" * 80)
        
        table_name = 'quotation_termsandcondition'
        
        # Check current column types
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
            AND column_name IN ('has_yellow_background', 'is_active')
        """, [table_name])
        
        columns = cursor.fetchall()
        print(f"\nCurrent column types in {table_name}:")
        for col_name, data_type in columns:
            print(f"  - {col_name}: {data_type}")
        
        # Fix has_yellow_background
        print("\n1. Converting 'has_yellow_background' from bit varying to boolean...")
        try:
            # Step 1: Add a temporary column with boolean type
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN has_yellow_background_temp BOOLEAN DEFAULT FALSE
            """)
            print("   ✓ Added temporary column")
            
            # Step 2: Convert bit varying values to boolean
            cursor.execute(f"""
                UPDATE {table_name} 
                SET has_yellow_background_temp = CASE 
                    WHEN has_yellow_background::text = '1' OR has_yellow_background::text = 't' THEN TRUE
                    WHEN has_yellow_background::text = '0' OR has_yellow_background::text = 'f' THEN FALSE
                    ELSE FALSE
                END
            """)
            print("   ✓ Converted values")
            
            # Step 3: Drop old column
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                DROP COLUMN has_yellow_background
            """)
            print("   ✓ Dropped old column")
            
            # Step 4: Rename temporary column
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                RENAME COLUMN has_yellow_background_temp TO has_yellow_background
            """)
            print("   ✓ Renamed temporary column")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            # If column already exists or is already boolean, try direct conversion
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ALTER COLUMN has_yellow_background TYPE BOOLEAN 
                    USING CASE 
                        WHEN has_yellow_background::text = '1' OR has_yellow_background::text = 't' THEN TRUE
                        WHEN has_yellow_background::text = '0' OR has_yellow_background::text = 'f' THEN FALSE
                        ELSE FALSE
                    END
                """)
                print("   ✓ Converted directly")
            except Exception as e2:
                print(f"   ✗ Direct conversion also failed: {e2}")
        
        # Fix is_active
        print("\n2. Converting 'is_active' from bit varying to boolean...")
        try:
            # Step 1: Add a temporary column with boolean type
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN is_active_temp BOOLEAN DEFAULT TRUE
            """)
            print("   ✓ Added temporary column")
            
            # Step 2: Convert bit varying values to boolean
            cursor.execute(f"""
                UPDATE {table_name} 
                SET is_active_temp = CASE 
                    WHEN is_active::text = '1' OR is_active::text = 't' THEN TRUE
                    WHEN is_active::text = '0' OR is_active::text = 'f' THEN FALSE
                    ELSE TRUE
                END
            """)
            print("   ✓ Converted values")
            
            # Step 3: Drop old column
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                DROP COLUMN is_active
            """)
            print("   ✓ Dropped old column")
            
            # Step 4: Rename temporary column
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                RENAME COLUMN is_active_temp TO is_active
            """)
            print("   ✓ Renamed temporary column")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            # If column already exists or is already boolean, try direct conversion
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ALTER COLUMN is_active TYPE BOOLEAN 
                    USING CASE 
                        WHEN is_active::text = '1' OR is_active::text = 't' THEN TRUE
                        WHEN is_active::text = '0' OR is_active::text = 'f' THEN FALSE
                        ELSE TRUE
                    END
                """)
                print("   ✓ Converted directly")
            except Exception as e2:
                print(f"   ✗ Direct conversion also failed: {e2}")
        
        # Verify the changes
        print("\n3. Verifying column types...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
            AND column_name IN ('has_yellow_background', 'is_active')
        """, [table_name])
        
        columns = cursor.fetchall()
        print(f"\nFinal column types in {table_name}:")
        for col_name, data_type in columns:
            print(f"  - {col_name}: {data_type}")
            if data_type != 'boolean':
                print(f"    ⚠ WARNING: {col_name} is still {data_type}, not boolean!")
            else:
                print(f"    ✓ OK")
        
        print("\n" + "=" * 80)
        print("FIX COMPLETE!")
        print("=" * 80)
        print("\nPlease restart your Django server for changes to take effect.")

if __name__ == '__main__':
    fix_quotation_boolean_fields()
