#!/usr/bin/env python
"""
Check if database id columns have DEFAULT values set
Run this to verify if the fix has been applied
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection

TABLES = [
    'customer_solarpump',
    'customer_controller',
    'customer_meters',
    'customer_generationmeter',
]

print("\n" + "="*80)
print("CHECKING DATABASE STATUS")
print("="*80)

with connection.cursor() as cursor:
    for table_name in TABLES:
        print(f"\n{table_name}:")
        cursor.execute(f"""
            SELECT column_name, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = 'id';
        """)
        result = cursor.fetchone()
        if result:
            col_name, col_default, is_nullable = result
            print(f"  Default: {col_default}")
            print(f"  Nullable: {is_nullable}")
            
            if col_default and 'nextval' in str(col_default) and is_nullable == 'NO':
                print(f"  Status: ✓ FIXED (has default value)")
            else:
                print(f"  Status: ✗ NOT FIXED (needs default value)")
                print(f"  ACTION NEEDED: Run FIX_DATABASE_NOW.py")
        else:
            print(f"  Status: ✗ Column 'id' not found")

print("\n" + "="*80)
print("If any table shows 'NOT FIXED', run: python FIX_DATABASE_NOW.py")
print("="*80 + "\n")

