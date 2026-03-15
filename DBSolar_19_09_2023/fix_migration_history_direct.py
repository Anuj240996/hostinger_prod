#!/usr/bin/env python
"""
Directly fix migration history in database by updating timestamps
This will make 0032 appear before 0045
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection
from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime

print("\n" + "="*80)
print("FIXING MIGRATION HISTORY - Direct Database Update")
print("="*80)

with connection.cursor() as cursor:
    # Get 0045 timestamp
    cursor.execute("""
        SELECT applied FROM django_migrations 
        WHERE app = 'customer' AND name = '0045_merge_20260104_1419';
    """)
    mig_0045 = cursor.fetchone()
    
    if mig_0045:
        mig_0045_time = mig_0045[0]
        print(f"\nFound 0045_merge_20260104_1419 applied at: {mig_0045_time}")
        
        # Convert to datetime if it's a string
        if isinstance(mig_0045_time, str):
            mig_0045_time = parse_datetime(mig_0045_time)
        if mig_0045_time is None:
            mig_0045_time = timezone.now()
        
        # Set 0032 to be 1 second before 0045
        new_time = mig_0045_time - timedelta(seconds=1)
        print(f"Setting 0032 timestamp to: {new_time}")
        
        cursor.execute("""
            UPDATE django_migrations 
            SET applied = %s
            WHERE app = 'customer' AND name = '0032_fix_all_id_columns';
        """, [new_time])
        
        if cursor.rowcount > 0:
            print("✓ Migration 0032 timestamp updated")
        else:
            print("⚠ Migration 0032 not found - inserting it...")
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied)
                VALUES ('customer', '0032_fix_all_id_columns', %s);
            """, [new_time])
            print("✓ Migration 0032 inserted")
    else:
        print("\n⚠ Migration 0045_merge_20260104_1419 not found")
        print("Inserting 0032 with current timestamp...")
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('customer', '0032_fix_all_id_columns', %s)
            ON CONFLICT DO NOTHING;
        """, [timezone.now()])
        print("✓ Migration 0032 inserted")
    
    # Verify
    print("\nVerifying migration order...")
    cursor.execute("""
        SELECT name, applied FROM django_migrations 
        WHERE app = 'customer' AND (name LIKE '0032%' OR name = '0045_merge_20260104_1419')
        ORDER BY applied;
    """)
    results = cursor.fetchall()
    for name, applied in results:
        print(f"  {name}: {applied}")

print("\n" + "="*80)
print("Migration history fixed!")
print("Now try: python manage.py makemigrations")
print("="*80 + "\n")

