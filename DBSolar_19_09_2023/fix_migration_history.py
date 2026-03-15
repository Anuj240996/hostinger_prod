#!/usr/bin/env python
"""
Fix inconsistent migration history
This will mark the missing migration as applied
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
print("FIXING MIGRATION HISTORY")
print("="*80)

with connection.cursor() as cursor:
    # Check if 0045 exists in database
    cursor.execute("""
        SELECT name FROM django_migrations 
        WHERE app = 'customer' AND name = '0045_merge_20260104_1419';
    """)
    result = cursor.fetchone()
    
    if not result:
        print("\nMigration 0045_merge_20260104_1419 is missing from database.")
        print("Adding it to django_migrations table...")
        
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('customer', '0045_merge_20260104_1419', %s)
            ON CONFLICT DO NOTHING;
        """, [timezone.now()])
        
        print("✓ Migration 0045 marked as applied")
    else:
        print("\nMigration 0045 already exists in database.")
    
    # Check current migration state
    print("\nCurrent migration state:")
    cursor.execute("""
        SELECT name FROM django_migrations 
        WHERE app = 'customer' 
        ORDER BY name DESC 
        LIMIT 10;
    """)
    migrations = cursor.fetchall()
    for mig in migrations:
        print(f"  - {mig[0]}")

print("\n" + "="*80)
print("Now try running: python manage.py migrate")
print("="*80 + "\n")

