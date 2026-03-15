"""
Fix migration order issue in customer app
Migration 0020 was applied before 0019, but 0020 depends on 0019
"""
import django
import os
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DBSolar_19_09_2023.inventoryproject.settings')

django.setup()

from django.db import connection

print("=" * 60)
print("Checking migration status...")
print("=" * 60)

# Check current migration status
cursor = connection.cursor()
cursor.execute("""
    SELECT app, name, applied 
    FROM django_migrations 
    WHERE app = 'customer' 
    AND name IN ('0019_alter_controller_assignby_alter_controller_assignto_and_more', '0020_alter_customer_cust_id')
    ORDER BY name;
""")

migrations = cursor.fetchall()
print("\nCurrent migration records:")
for app, name, applied in migrations:
    print(f"  {name}: Applied at {applied}")

# Check if 0019 is missing
cursor.execute("""
    SELECT COUNT(*) 
    FROM django_migrations 
    WHERE app = 'customer' 
    AND name = '0019_alter_controller_assignby_alter_controller_assignto_and_more';
""")

count_0019 = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) 
    FROM django_migrations 
    WHERE app = 'customer' 
    AND name = '0020_alter_customer_cust_id';
""")

count_0020 = cursor.fetchone()[0]

print("\n" + "=" * 60)
print("Migration Status:")
print("=" * 60)
print(f"  0019 exists: {count_0019 > 0}")
print(f"  0020 exists: {count_0020 > 0}")

if count_0020 > 0 and count_0019 == 0:
    print("\n❌ Problem found: 0020 is applied but 0019 is missing!")
    print("\nSolution: We need to fake migration 0019")
    print("\nRun this command:")
    print("  python manage.py migrate customer 0019 --fake")
    print("\nThis will mark 0019 as applied without running it.")
    print("(The database changes from 0019 are likely already applied)")
elif count_0019 > 0 and count_0020 > 0:
    print("\n✅ Both migrations exist in database")
    print("The error might be about the order. Check the applied dates above.")
    print("\nIf 0020's applied date is before 0019's, you need to:")
    print("  1. Delete 0020 from django_migrations table")
    print("  2. Re-apply it with: python manage.py migrate customer 0020")
else:
    print("\n⚠️  Unexpected state. Check the migration records manually.")

cursor.close()
