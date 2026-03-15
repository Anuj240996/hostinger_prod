#!/usr/bin/env python
"""
Directly fix migration history in database
This will check and fix the 0045/0046 issue
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
print("FIXING MIGRATION HISTORY - Direct Database Fix")
print("="*80)

with connection.cursor() as cursor:
    # Check what migrations exist
    print("\nChecking migration 0045...")
    cursor.execute("""
        SELECT name, applied FROM django_migrations 
        WHERE app = 'customer' AND name LIKE '0045%';
    """)
    mig_0045 = cursor.fetchall()
    if mig_0045:
        print(f"  Found: {mig_0045}")
    else:
        print("  Not found")
    
    print("\nChecking migration 0046...")
    cursor.execute("""
        SELECT name, applied FROM django_migrations 
        WHERE app = 'customer' AND name LIKE '0046%';
    """)
    mig_0046 = cursor.fetchall()
    if mig_0046:
        print(f"  Found: {mig_0046}")
    else:
        print("  Not found")
    
    # If 0046 exists but 0045 doesn't, we need to add 0045
    if mig_0046 and not mig_0045:
        print("\n⚠ Issue detected: 0046 exists but 0045 doesn't!")
        print("Adding 0045_merge_20260104_1419 to database...")
        
        # Get the applied time from 0046 (use it or earlier)
        cursor.execute("""
            SELECT applied FROM django_migrations 
            WHERE app = 'customer' AND name LIKE '0046%'
            LIMIT 1;
        """)
        result = cursor.fetchone()
        applied_time = result[0] if result else timezone.now()
        
        # Insert 0045 with an earlier timestamp
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('customer', '0045_merge_20260104_1419', %s)
            ON CONFLICT DO NOTHING;
        """, [applied_time])
        
        print("✓ Migration 0045 added to database")
    
    # If both exist, check their order
    elif mig_0045 and mig_0046:
        print("\nBoth migrations exist. Checking order...")
        cursor.execute("""
            SELECT name, applied FROM django_migrations 
            WHERE app = 'customer' AND (name LIKE '0045%' OR name LIKE '0046%')
            ORDER BY applied;
        """)
        order = cursor.fetchall()
        print(f"  Applied order: {order}")
        
        # If 0046 was applied before 0045, update 0045 to be earlier
        if len(order) == 2 and '0046' in order[1][0]:
            print("\n⚠ Issue: 0046 was applied before 0045!")
            print("Updating 0045 timestamp to be before 0046...")
            
            cursor.execute("""
                SELECT applied FROM django_migrations 
                WHERE app = 'customer' AND name LIKE '0046%'
                LIMIT 1;
            """)
            mig_0046_time = cursor.fetchone()[0]
            
            # Set 0045 to be 1 second earlier
            from datetime import timedelta
            new_time = mig_0046_time - timedelta(seconds=1)
            
            cursor.execute("""
                UPDATE django_migrations 
                SET applied = %s
                WHERE app = 'customer' AND name LIKE '0045%';
            """, [new_time])
            
            print("✓ Migration 0045 timestamp updated")

print("\n" + "="*80)
print("Migration history fixed!")
print("Now try: python manage.py migrate")
print("="*80 + "\n")

