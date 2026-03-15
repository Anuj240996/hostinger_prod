#!/bin/bash
# Quick fix script - removes problematic files and fixes id columns

cd /home/anujdeshmukh24/DBSolar_19_09_2023/DBSolar_19_09_2023

echo "Removing problematic migration files..."
rm -f customer/migrations/fix_migration_history.py
rm -f customer/migrations/fix_migration_direct.py
rm -f fix_migration_history.py
rm -f fix_migration_direct.py

echo "Files removed. Now fixing id columns..."
source /home/anujdeshmukh24/env/bin/activate
python FIX_DATABASE_NOW.py

echo ""
echo "Done! Now restart your Django server:"
echo "python manage.py runserver 0.0.0.0:8000"

