#!/usr/bin/env python
"""
Direct database fix script for quotation_termsandcondition boolean fields.
Run this script to convert bit varying columns to boolean type in PostgreSQL.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DBSolar_19_09_2023.settings')
django.setup()

from django.db import connection

def fix_quotation_booleans():
    """Convert bit varying columns to boolean in quotation_termsandcondition table"""
    
    print("=" * 80)
    print("FIXING QUOTATION TERMS AND CONDITION BOOLEAN FIELDS")
    print("=" * 80)
    
    try:
        with connection.cursor() as cursor:
            # Check current column types
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'quotation_termsandcondition' 
                AND column_name IN ('is_active', 'has_yellow_background')
            """)
            
            current_types = {row[0]: row[1] for row in cursor.fetchall()}
            print(f"\nCurrent column types: {current_types}")
            
            # Fix is_active column
            if 'is_active' in current_types:
                print(f"\nConverting is_active from {current_types['is_active']} to boolean...")
                cursor.execute("""
                    ALTER TABLE quotation_termsandcondition 
                    ALTER COLUMN is_active TYPE boolean 
                    USING CASE 
                        WHEN is_active::text IN ('1', 't', 'true', 'True', 'TRUE', 'y', 'yes', 'Y', 'YES') THEN true 
                        WHEN is_active::text IN ('0', 'f', 'false', 'False', 'FALSE', 'n', 'no', 'N', 'NO', '') THEN false 
                        ELSE false
                    END
                """)
                print("✓ is_active converted to boolean")
            
            # Fix has_yellow_background column
            if 'has_yellow_background' in current_types:
                print(f"\nConverting has_yellow_background from {current_types['has_yellow_background']} to boolean...")
                cursor.execute("""
                    ALTER TABLE quotation_termsandcondition 
                    ALTER COLUMN has_yellow_background TYPE boolean 
                    USING CASE 
                        WHEN has_yellow_background::text IN ('1', 't', 'true', 'True', 'TRUE', 'y', 'yes', 'Y', 'YES') THEN true 
                        WHEN has_yellow_background::text IN ('0', 'f', 'false', 'False', 'FALSE', 'n', 'no', 'N', 'NO', '') THEN false 
                        ELSE false
                    END
                """)
                print("✓ has_yellow_background converted to boolean")
            
            # Verify the changes
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'quotation_termsandcondition' 
                AND column_name IN ('is_active', 'has_yellow_background')
            """)
            
            new_types = {row[0]: row[1] for row in cursor.fetchall()}
            print(f"\nNew column types: {new_types}")
            
            print("\n" + "=" * 80)
            print("✓ SUCCESS: Boolean fields have been converted!")
            print("=" * 80)
            print("\nPlease restart your Django server for the changes to take effect.")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    fix_quotation_booleans()
