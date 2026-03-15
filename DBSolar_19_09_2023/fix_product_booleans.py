#!/usr/bin/env python
"""
Fix boolean fields in product and inventory app tables
Convert bit varying to boolean type
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection

print("\n" + "="*80)
print("FIXING BOOLEAN FIELDS (Product, Inventory, Transactions & Quotation)")
print("="*80)

# Tables with boolean columns
TABLES = [
    ('product_category', 'status'),
    ('product_subcategory', 'status'), 
    ('product_product', 'status'),
    ('product_brand', 'status'),
    ('inventory_stock', 'status'),
    ('inventory_stock', 'is_deleted'),
    ('transactions_supplier', 'status'),
    ('transactions_supplier', 'is_deleted'),
    ('transactions_vendor', 'status'),
    ('transactions_vendor', 'is_deleted'),
    ('quotation_termsandcondition', 'has_yellow_background'),
    ('quotation_termsandcondition', 'is_active'),
]

with connection.cursor() as cursor:
    for table_name, column_name in TABLES:
        print(f"\n>>> Fixing {table_name}.{column_name}...")
        try:
            # Check if column exists
            cursor.execute(f"""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = '{column_name}';
            """)
            result = cursor.fetchone()
            
            if not result:
                print(f"   ⚠ Column '{column_name}' not found in {table_name}, skipping...")
                continue
                
            data_type = result[0]
            print(f"   Current type: {data_type}")
            
            if data_type == 'boolean':
                print(f"   ✓ {table_name}.{column_name} is already boolean, skipping...")
                continue
            
            # Convert to boolean
            # Handle bit varying by converting to text first, then to boolean
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ALTER COLUMN {column_name} TYPE boolean 
                USING CASE 
                    WHEN {column_name}::text = '1' OR {column_name}::text = 't' OR {column_name}::text = 'true' THEN true 
                    WHEN {column_name}::text = '0' OR {column_name}::text = 'f' OR {column_name}::text = 'false' THEN false 
                    WHEN {column_name} IS NULL THEN NULL 
                    ELSE ({column_name}::text)::boolean 
                END;
            """)
            
            print(f"   ✓ {table_name}.{column_name} converted to boolean!")
            
        except Exception as e:
            print(f"   ✗ ERROR fixing {table_name}.{column_name}: {str(e)}")
            # Continue with other tables even if one fails
            continue

print("\n" + "="*80)
print("FIX COMPLETE!")
print("="*80)
print("\nIMPORTANT: Restart your Django server if it's running!")
print("="*80 + "\n")

