#!/usr/bin/env python
"""
Fake-apply migration 0047 since database columns already exist in lowercase
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
        print(f"\n✓ Migration {existing[0]} already exists in database.")
    else:
        # Use the exact name from the error
        migration_name = '0047_alter_customer_cust_id_and_more'
        print(f"\nAdding {migration_name} to database...")
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('customer', %s, %s);
        """, [migration_name, timezone.now()])
        print(f"✓ Migration {migration_name} marked as applied (fake)")

print("\n" + "="*80)
print("Migration 0047 fake-applied!")
print("Now try: python manage.py migrate")
print("="*80 + "\n")

