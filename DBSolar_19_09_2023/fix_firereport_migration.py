#!/usr/bin/env python
"""
Fix for firereport migration issue.
The migration is trying to alter a column that doesn't exist in lowercase.
Since the model already has db_column='Location', we should fake this migration.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DBSolar_19_09_2023.settings')
django.setup()

from django.db import connection

def check_and_fix_migration():
    """Check if migration needs to be fixed"""
    
    print("=" * 80)
    print("CHECKING FIREREPORT MIGRATION ISSUE")
    print("=" * 80)
    
    try:
        with connection.cursor() as cursor:
            # Check if Location column exists (uppercase)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'firereport_firereport' 
                AND column_name = 'Location'
            """)
            
            location_exists = cursor.fetchone()
            
            # Check if location column exists (lowercase)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'firereport_firereport' 
                AND column_name = 'location'
            """)
            
            location_lower_exists = cursor.fetchone()
            
            print(f"\nDatabase column 'Location' (uppercase) exists: {location_exists is not None}")
            print(f"Database column 'location' (lowercase) exists: {location_lower_exists is not None}")
            
            if location_exists and not location_lower_exists:
                print("\n✓ Database has 'Location' (uppercase) column - this is correct")
                print("✓ The migration can be faked since the database already matches the model")
                print("\nRun this command to fake the migration:")
                print("  python manage.py migrate firereport 0003 --fake")
            else:
                print("\n⚠ Database column state is unexpected")
                if location_lower_exists:
                    print("  - Lowercase 'location' column exists - this needs to be renamed")
                if not location_exists:
                    print("  - Uppercase 'Location' column does not exist - this is a problem")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    check_and_fix_migration()
