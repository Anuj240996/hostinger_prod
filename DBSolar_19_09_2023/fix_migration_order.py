#!/usr/bin/env python
"""
Fix migration order - ensure 0032 is applied before 0045
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection
from datetime import timedelta

print("\n" + "="*80)
print("FIXING MIGRATION ORDER")
print("="*80)

with connection.cursor() as cursor:
    # Check if 0032 exists
    cursor.execute("""
        SELECT name, applied FROM django_migrations 
        WHERE app = 'customer' AND name LIKE '0032%';
    """)
    mig_0032 = cursor.fetchone()
    
    # Check if 0045 exists
    cursor.execute("""
        SELECT name, applied FROM django_migrations 
        WHERE app = 'customer' AND name = '0045_merge_20260104_1419';
    """)
    mig_0045 = cursor.fetchone()
    
    if mig_0032 and mig_0045:
        print(f"\n0032 found: {mig_0032}")
        print(f"0045 found: {mig_0045}")
        
        # If 0045 was applied before 0032, fix the order
        if mig_0045[1] < mig_0032[1]:
            print("\n⚠ Issue: 0045 was applied before 0032!")
            print("Fixing order...")
            
            # Set 0032 to be 1 second before 0045
            new_time = mig_0045[1] - timedelta(seconds=1)
            
            cursor.execute("""
                UPDATE django_migrations 
                SET applied = %s
                WHERE app = 'customer' AND name LIKE '0032%';
            """, [new_time])
            
            print(f"✓ Updated 0032 timestamp to {new_time}")
        else:
            print("\n✓ Migration order is correct (0032 before 0045)")
    elif not mig_0032:
        print("\n⚠ Migration 0032 not found in database")
        print("You may need to apply it first or fake it")
    elif not mig_0045:
        print("\n⚠ Migration 0045 not found in database")

print("\n" + "="*80)
print("Migration order fixed!")
print("Now try: python manage.py makemigrations")
print("="*80 + "\n")

