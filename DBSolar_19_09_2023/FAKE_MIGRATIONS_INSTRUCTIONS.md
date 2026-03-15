# Instructions to Fake Migrations

The migrations are trying to rename columns that already exist with the correct lowercase names in PostgreSQL. Since we've updated the models to use `db_column` pointing to the existing columns, we need to **fake** these migrations (mark them as applied without actually running them).

## Solution: Fake the Migrations

Run these commands on your server:

```bash
cd /home/anujdeshmukh24/DBSolar_19_09_2023/DBSolar_19_09_2023

# Fake the customer migration
python manage.py migrate customer 0019 --fake

# Fake the detect_barcodes migration  
python manage.py migrate detect_barcodes 0003 --fake

# Fake the firereport migration
python manage.py migrate firereport 0002 --fake

# Fake the user migration
python manage.py migrate user 0002 --fake
```

Or fake all of them at once:

```bash
python manage.py migrate customer 0019 --fake
python manage.py migrate detect_barcodes 0003 --fake
python manage.py migrate firereport 0002 --fake
python manage.py migrate user 0002 --fake
```

## Why This Works

- The database columns already have lowercase names (e.g., `assignby_id`, `assignto_id`)
- We've updated the models to use `db_column` pointing to these existing columns
- Django thinks it needs to rename columns, but they're already correct
- Faking the migrations tells Django "these changes are already applied" without actually running them

## After Faking

After faking the migrations, verify everything works:

```bash
# Check migration status
python manage.py showmigrations

# Try accessing your application
# The Internal Server Error should be resolved
```

## Alternative: If Faking Doesn't Work

If you still get errors, you can delete the migration files and recreate them as no-ops:

```bash
# Delete the problematic migration files
rm customer/migrations/0019_*.py
rm detect_barcodes/migrations/0003_*.py
rm firereport/migrations/0002_*.py
rm user/migrations/0002_*.py

# Then mark them as applied in the database
python manage.py migrate --fake customer
python manage.py migrate --fake detect_barcodes
python manage.py migrate --fake firereport
python manage.py migrate --fake user
```

