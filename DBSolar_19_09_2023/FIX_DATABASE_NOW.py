#!/usr/bin/env python
"""
SIMPLE DATABASE FIX - Run this on your server to fix ALL id column errors
This will fix: solarpump, controller, meters, generationmeter, inspectiondetail, favoritelist, barcodeimage, inverterimage, category, subcategory, product, unit, supplier, brand, transactions_supplier, transactions_vendor
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventoryproject.settings')
django.setup()

from django.db import connection

# All tables that need fixing
TABLES = [
    ('customer_solarpump', 'customer_solarpump_id_seq', 'customer_solarpump_pkey'),
    ('customer_controller', 'customer_controller_id_seq', 'customer_controller_pkey'),
    ('customer_meters', 'customer_meters_id_seq', 'customer_meters_pkey'),
    ('customer_generationmeter', 'customer_generationmeter_id_seq', 'customer_generationmeter_pkey'),
    ('customer_inspectiondetail', 'customer_inspectiondetail_id_seq', 'customer_inspectiondetail_pkey'),
    ('inventory_favoritelist', 'inventory_favoritelist_id_seq', 'inventory_favoritelist_pkey'),
    ('detect_barcodes_barcodeimage', 'detect_barcodes_barcodeimage_id_seq', 'detect_barcodes_barcodeimage_pkey'),
    ('detect_barcodes_inverterimage', 'detect_barcodes_inverterimage_id_seq', 'detect_barcodes_inverterimage_pkey'),
    ('product_category', 'product_category_id_seq', 'product_category_pkey'),
    ('product_subcategory', 'product_subcategory_id_seq', 'product_subcategory_pkey'),
    ('product_product', 'product_product_id_seq', 'product_product_pkey'),
    ('product_unit', 'product_unit_id_seq', 'product_unit_pkey'),
    ('product_supplier', 'product_supplier_id_seq', 'product_supplier_pkey'),
    ('product_brand', 'product_brand_id_seq', 'product_brand_pkey'),
    ('transactions_supplier', 'transactions_supplier_id_seq', 'transactions_supplier_pkey'),
    ('transactions_vendor', 'transactions_vendor_id_seq', 'transactions_vendor_pkey'),
]

print("\n" + "="*80)
print("DATABASE FIX SCRIPT - Fixing all id column issues")
print("="*80)

with connection.cursor() as cursor:
    for table_name, seq_name, pkey_name in TABLES:
        print(f"\n>>> Fixing {table_name}...")
        try:
            # Step 1: Drop PK if exists
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {pkey_name};")
            
            # Step 2: Drop sequence if exists
            cursor.execute(f"DROP SEQUENCE IF EXISTS {seq_name} CASCADE;")
            
            # Step 3: Create sequence
            cursor.execute(f"CREATE SEQUENCE {seq_name};")
            
            # Step 4: Update NULL ids
            cursor.execute(f"UPDATE {table_name} SET id = nextval('{seq_name}') WHERE id IS NULL;")
            updated = cursor.rowcount
            print(f"   Updated {updated} NULL id values")
            
            # Step 5: Set sequence value
            cursor.execute(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {table_name}), 0) + 1, false);")
            
            # Step 6: Set NOT NULL
            cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET NOT NULL;")
            
            # Step 7: Set DEFAULT (THIS IS THE KEY!)
            cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET DEFAULT nextval('{seq_name}');")
            
            # Step 8: Add PK
            cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {pkey_name} PRIMARY KEY (id);")
            
            # Step 9: Set ownership
            cursor.execute(f"ALTER SEQUENCE {seq_name} OWNED BY {table_name}.id;")
            
            print(f"   ✓ {table_name} FIXED!")
            
        except Exception as e:
            print(f"   ✗ ERROR fixing {table_name}: {str(e)}")
            # Continue with other tables even if one fails
            continue

print("\n" + "="*80)
print("FIX COMPLETE!")
print("="*80)
print("\nIMPORTANT: You MUST restart your Django server now!")
print("1. Stop server (Ctrl+C)")
print("2. Restart: python manage.py runserver 0.0.0.0:8000")
print("="*80 + "\n")

