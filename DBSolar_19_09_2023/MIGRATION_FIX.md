# How to Fix Migration Errors

## Problem

You're getting this error:
```
django.db.utils.ProgrammingError: column "id" of relation "firereport_firereport" is an identity column
```

This happens because PostgreSQL 10+ uses "identity columns" which automatically handle sequences, and the migration is trying to set a DEFAULT which conflicts with identity columns.

## Solution

### Option 1: Fake the Problematic Migration (Quick Fix)

If the database already has the correct structure, you can mark the migration as applied without running it:

```bash
python manage.py migrate firereport 0004 --fake
```

Then continue with other migrations:
```bash
python manage.py migrate
```

### Option 2: Use the Fixed Migration (Recommended)

I've already fixed the migration file `0004_fix_firereport_id_sequence.py` to handle identity columns. After pulling the latest code:

1. **Rebuild your Docker image** (to get the fixed migration)
2. **Run migrations again:**
   ```bash
   python manage.py migrate
   ```

### Option 3: Skip Problematic Migrations

If you want to skip migrations that are causing issues:

```bash
# Fake apply the problematic migration
python manage.py migrate firereport 0004 --fake

# Then continue with other migrations
python manage.py migrate
```

## What I Fixed

1. **Updated `0004_fix_firereport_id_sequence.py`:**
   - Added check for identity columns
   - Skips ALTER TABLE if column is already an identity column
   - Handles errors gracefully

2. **Updated `entrypoint.sh`:**
   - Better error handling for migrations
   - Attempts fake migration if regular migration fails

## Steps to Apply Fix

1. **Pull latest code** (if not already done)
2. **Rebuild Docker image** in Easypanel
3. **After container starts, run migrations manually if needed:**
   ```bash
   python manage.py migrate
   ```

## If Migrations Still Fail

You can fake all remaining migrations if the database structure is already correct:

```bash
python manage.py migrate --fake
```

**Warning:** Only use `--fake` if you're sure the database structure matches what Django expects!
