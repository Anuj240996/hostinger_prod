# Easy Step-by-Step Guide to Fix Easypanel Configuration

## What You Need to Fix

Your webapp service needs 3 fixes:
1. Change database port from 5432 to 2700
2. Change domain port from 80 to 8000
3. Add missing environment variables

---

## Step-by-Step Instructions

### Step 1: Open Your Easypanel Dashboard
1. Go to your Easypanel dashboard
2. Find your project: **db_solar**
3. Click on the **webapp** service

### Step 2: Fix the Database Connection

1. **Find "Environment Variables" or "Env" section**
   - Look for `DATABASE_URL` in the environment variables

2. **Update DATABASE_URL:**
   - **Current:** `postgres://heramb:Heramb2023@db_solar_database:5432/db_solar`
   - **Change to:** `postgresql://heramb:Heramb2023@db_solar_database:2700/db_solar`
   - **What changed:** 
     - `postgres://` → `postgresql://`
     - `:5432` → `:2700`

### Step 3: Add Missing Environment Variables

In the same "Environment Variables" section, **ADD** these new variables:

1. **SECRET_KEY**
   - Name: `SECRET_KEY`
   - Value: `your-secret-key-here-change-this-to-random-string`
   - ⚠️ **Important:** Generate a random secret key (you can use: https://djecrety.ir/ or any random string generator)

2. **ALLOWED_HOSTS**
   - Name: `ALLOWED_HOSTS`
   - Value: `db-solar.co.in,www.db-solar.co.in,72.60.98.248,db-solar-webapp.fhibgf.easypanel.host`

3. **DEBUG**
   - Name: `DEBUG`
   - Value: `False`

### Step 4: Fix Domain Port

1. **Find "Domains" or "Domain" section**
   - Look for your domain: `db-solar-webapp.fhibgf.easypanel.host`

2. **Change the Port:**
   - **Current:** Port `80`
   - **Change to:** Port `8000`
   - This should be in the domain settings

### Step 5: Save and Restart

1. **Click "Save" or "Update"** button
2. **Restart the service:**
   - Look for "Restart" or "Redeploy" button
   - Click it to apply changes

---

## Quick Checklist

After making changes, verify:

- [ ] DATABASE_URL uses port `2700` (not 5432)
- [ ] DATABASE_URL uses `postgresql://` (not `postgres://`)
- [ ] SECRET_KEY is added and set to a random value
- [ ] ALLOWED_HOSTS is added with all your domains
- [ ] DEBUG is set to `False`
- [ ] Domain port is `8000` (not 80)
- [ ] Service has been restarted

---

## What Your Final Environment Variables Should Look Like

```
DATABASE_URL=postgresql://heramb:Heramb2023@db_solar_database:2700/db_solar
SECRET_KEY=your-random-secret-key-here
ALLOWED_HOSTS=db-solar.co.in,www.db-solar.co.in,72.60.98.248,db-solar-webapp.fhibgf.easypanel.host
DEBUG=False
```

---

## After Restarting - Check These

1. **Check Logs:**
   - Look for "Database connection successful!" message
   - No connection errors

2. **Test Your Website:**
   - Visit your domain
   - Check if logos/images are showing
   - Try logging in

3. **If Something Doesn't Work:**
   - Check the logs for error messages
   - Verify all environment variables are saved correctly
   - Make sure the service restarted successfully

---

## Need Help?

If you get stuck:
1. Check the container logs in Easypanel
2. Verify all environment variables are exactly as shown above
3. Make sure the database service is running
4. Check that port 2700 is accessible from your webapp service
