#!/usr/bin/env python
"""
Fake-apply migration 0047 since the database columns already exist
(they're just in lowercase, which matches our db_column mappings)
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection
from django.utils import timezone

print("\n" + "="*80)
print("FAKE-APPLYING MIGRATION 0047")
print("="*80)

with connection.cursor() as cursor:
    # Check if 0047 already exists
    cursor.execute("""
        SELECT name FROM django_migrations 
        WHERE app = 'customer' AND name LIKE '0047%';
    """)
    existing = cursor.fetchone()
    
    if existing:
        print(f"\nMigration {existing[0]} already exists in database.")
    else:
        # Get the actual migration name from the migrations directory
        import glob
        migration_files = glob.glob('customer/migrations/0047*.py')
        if migration_files:
            migration_name = os.path.basename(migration_files[0]).replace('.py', '')
            print(f"\nFound migration file: {migration_name}")
            print(f"Adding {migration_name} to database...")
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('customer', %s, %s);
            """, [migration_name, timezone.now()])
            print(f"✓ Migration {migration_name} marked as applied")
        else:
            # Fallback to the name from the error
            migration_name = '0047_alter_customer_cust_id_and_more'
            print(f"\nAdding {migration_name} to database...")
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('customer', %s, %s);
            """, [migration_name, timezone.now()])
            print(f"✓ Migration {migration_name} marked as applied")

print("\n" + "="*80)
print("Migration 0047 fake-applied!")
print("Now try: python manage.py migrate")
print("="*80 + "\n")

