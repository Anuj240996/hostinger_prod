# How to Log In to Your Django Web App

## The Problem

Your database has existing users, but **passwords are encrypted/hashed** in the database, so you can't see the actual passwords.

## Solution: Create a New Superuser

The easiest way is to create a new admin user with a password you know.

### Option 1: Create Superuser via Easypanel (Recommended)

1. **Go to Easypanel Dashboard**
2. **Open your webapp service**
3. **Find "Terminal" or "Console" or "Execute Command" option**
4. **Run this command:**
   ```bash
   python manage.py createsuperuser
   ```
5. **Follow the prompts:**
   - Username: (enter any username, e.g., `admin`)
   - Email: (enter your email, e.g., `admin@db-solar.co.in`)
   - Password: (enter a password you'll remember)
   - Password (again): (confirm the password)

### Option 2: Create Superuser via Docker Exec

If you have direct access to the container:

```bash
docker exec -it <container-name> python manage.py createsuperuser
```

### Option 3: Add Command to Entrypoint (Temporary)

You can temporarily add this to your entrypoint.sh to auto-create a user (remove after first use):

```bash
python manage.py createsuperuser --noinput --username admin --email admin@db-solar.co.in || echo "User may already exist"
```

**Note:** This won't set a password automatically, so you'd need to reset it.

## Reset Password for Existing User

If you know a username from your database, you can reset its password:

1. **Open Terminal/Console in Easypanel**
2. **Run:**
   ```bash
   python manage.py changepassword <username>
   ```
   Replace `<username>` with an actual username from your database.

## Find Existing Usernames

To see what users exist in your database, you can:

1. **Connect to your database** (via Easypanel database tools or psql)
2. **Run SQL query:**
   ```sql
   SELECT username, email, is_superuser, is_staff FROM auth_user;
   ```

## Quick Steps Summary

**Easiest Method:**
1. Go to Easypanel → webapp service
2. Open Terminal/Console
3. Run: `python manage.py createsuperuser`
4. Enter username, email, and password
5. Use those credentials to log in

## Default Login URL

After creating a user, go to:
- **Main login:** `http://your-domain/` (root URL)
- **Admin panel:** `http://your-domain/admin/` (if you created a superuser)

## Common Usernames in Your Database

Based on your database, you might have users like:
- `Pankaj_10`
- `DB_JDeshmukh2023`
- `Riyaz_20`
- `DB_BHostel2023`
- `Akash_19`
- `Kunal_27`
- etc.

But you'll need to reset their passwords since they're encrypted.
