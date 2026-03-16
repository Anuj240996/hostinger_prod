# Easypanel Database Configuration Guide for db_solar

This guide will help you configure your existing PostgreSQL database (`db_solar` on port `2700`) with your Django application in Easypanel.

## Prerequisites

- PostgreSQL database service running on port `2700` in Easypanel
- Database name: `db_solar`
- Database SQL dump file: `db_solar.sql` (already exists)

## Step 1: Database Service Configuration in Easypanel

### If Database is Already Running:

1. **Go to your Database Service in Easypanel**
2. **Check the Service Details:**
   - Service Name: (e.g., `postgres-db-solar`)
   - Port: `2700` (should be configured)
   - Database Name: `db_solar`
   - Username: (your database user)
   - Password: (your database password)

### If You Need to Create/Configure Database Service:

1. **Create PostgreSQL Service:**
   - Service Type: PostgreSQL
   - Port: `2700` (custom port)
   - Database Name: `db_solar`
   - Set username and password

2. **Import Database (if needed):**
   - If the database is empty, you may need to import `db_solar.sql`
   - Use Easypanel's database management tools or connect via psql

## Step 2: Link Database to Your Django App

### Option A: Using Environment Variables (Recommended)

In your Django App service in Easypanel, add these environment variables:

```
DB_HOST=<your-postgres-service-name>
DB_PORT=2700
DB_NAME=db_solar
DB_USER=<your-db-username>
DB_PASSWORD=<your-db-password>
```

**OR** use Easypanel's standard naming:

```
POSTGRES_HOST=<your-postgres-service-name>
POSTGRES_PORT=2700
POSTGRES_DB=db_solar
POSTGRES_USER=<your-db-username>
POSTGRES_PASSWORD=<your-db-password>
```

### Option B: Using DATABASE_URL

If Easypanel provides a connection string:

```
DATABASE_URL=postgresql://username:password@service-name:2700/db_solar
```

## Step 3: Additional Environment Variables

Add these to your Django App service:

```
SECRET_KEY=<generate-a-secure-secret-key>
ALLOWED_HOSTS=db-solar.co.in,www.db-solar.co.in,72.60.98.248
DEBUG=False
```

## Step 4: Database Import (If Needed)

If your database is empty and you need to import `db_solar.sql`:

### Method 1: Using Easypanel Database Tools
1. Go to your PostgreSQL service
2. Use the database management interface
3. Import the SQL file

### Method 2: Using psql Command
```bash
# Connect to your database service
psql -h <service-host> -p 2700 -U <username> -d db_solar < db_solar.sql
```

## Step 5: Django Migrations

Since you have an existing database, you have two options:

### Option A: Use Existing Database (No Migrations)
If your database already has all the tables:
- The app will connect and use existing tables
- Make sure Django models match your database schema

### Option B: Run Migrations (If Schema Changed)
If you've made changes to models:
```bash
# In your Django app container
python manage.py migrate --run-syncdb
```

**Note:** Be careful with migrations on existing production database!

## Step 6: Verify Connection

After deployment, check logs to verify database connection:

1. **Check Container Logs:**
   - Look for "Database connection successful!" message
   - Check for any connection errors

2. **Test Database Connection:**
   - Access Django admin or any database-dependent page
   - Verify data is loading correctly

## Troubleshooting

### Connection Refused
- Verify `DB_HOST` matches your PostgreSQL service name in Easypanel
- Check that port `2700` is correct
- Ensure database service is running

### Authentication Failed
- Double-check username and password
- Verify user has access to `db_solar` database

### Database Not Found
- Verify database name is exactly `db_solar`
- Check if database exists: `psql -l`

### Port Issues
- Ensure port `2700` is exposed and accessible
- Check firewall/network settings in Easypanel

## Important Notes

1. **Database Port:** Your database uses port `2700` (not the default `5432`)
2. **Database Name:** Must be exactly `db_solar` (case-sensitive)
3. **Existing Data:** Your database already has data, so be careful with migrations
4. **Service Name:** In Easypanel, use the service name (not IP) for `DB_HOST`

## Quick Checklist

- [ ] PostgreSQL service running on port `2700`
- [ ] Database `db_solar` exists
- [ ] Environment variables set in Django app service
- [ ] Database service linked to Django app (if Easypanel supports linking)
- [ ] Database connection verified in logs
- [ ] Application can access database tables
