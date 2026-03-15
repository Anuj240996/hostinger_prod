#!/usr/bin/env python
"""
Script to fix or fake the firereport.0003 migration.
This migration tries to alter a 'location' column that doesn't exist.
The database already has 'Location' (uppercase) and the model has db_column='Location'.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DBSolar_19_09_2023.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def fix_migration():
    """Fix the migration by faking it"""
    
    print("=" * 80)
    print("FIXING FIREREPORT MIGRATION 0003")
    print("=" * 80)
    
    try:
        # Check current migration state
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'firereport_firereport' 
                AND column_name IN ('Location', 'location')
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print(f"\nDatabase columns: {columns}")
        
        # Check if migration is already applied
        from django.db.migrations.recorder import MigrationRecorder
        recorder = MigrationRecorder(connection)
        try:
            applied = recorder.applied_migrations().filter(
                app='firereport',
                name='0003_alter_firereport_location'
            ).exists()
            
            if applied:
                print("\n✓ Migration 0003 is already marked as applied")
                print("  If you're still getting errors, try: python manage.py migrate firereport 0002 --fake")
                return True
        except:
            pass
        
        print("\n→ Faking migration 0003...")
        print("  (The database already has the correct 'Location' column)")
        
        # Fake the migration
        call_command('migrate', 'firereport', '0003', '--fake', verbosity=2)
        
        print("\n✓ Migration 0003 has been faked successfully!")
        print("  You can now run: python manage.py migrate")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("MANUAL FIX INSTRUCTIONS:")
        print("=" * 80)
        print("\nIf the script failed, run this command manually:")
        print("  python manage.py migrate firereport 0003 --fake")
        print("\nThen continue with:")
        print("  python manage.py migrate")
        
        return False

if __name__ == '__main__':
    fix_migration()
