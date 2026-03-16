# Easypanel Configuration Issues and Fixes

## Issues Found in Your Current Configuration

### 1. **Database Port Mismatch** ⚠️ CRITICAL
- **Current**: `DATABASE_URL` uses port `5432`
- **Expected**: Port `2700` (as per your database setup)
- **Fix**: Update DATABASE_URL to use port `2700`

### 2. **Database Service Port Not Configured**
- **Current**: Database service doesn't specify port mapping
- **Issue**: If database is on port 2700, it needs to be exposed
- **Fix**: Add port mapping to database service

### 3. **Domain Port Mismatch**
- **Current**: Domain points to port `80`
- **Expected**: Should point to port `8000` (your app's port)
- **Fix**: Update domain port to `8000`

### 4. **Missing Environment Variables**
- **Current**: Only `DATABASE_URL` is set
- **Missing**: `SECRET_KEY`, `ALLOWED_HOSTS`, `DEBUG`
- **Fix**: Add all required environment variables

### 5. **DATABASE_URL Format**
- **Current**: Uses `postgres://` (deprecated)
- **Better**: Use `postgresql://` (recommended format)
- **Fix**: Update to `postgresql://`

## Corrected Configuration

### Database Service
```json
{
  "type": "postgres",
  "data": {
    "projectName": "db_solar",
    "serviceName": "database",
    "image": "postgres:17",
    "password": "Heramb2023",
    "ports": [
      {
        "published": 2700,
        "target": 5432,
        "protocol": "tcp"
      }
    ]
  }
}
```

**Note**: If your database is already running on port 2700 externally, you may not need this port mapping. The internal service name `db_solar_database` will resolve to the service.

### Web App Service - Corrected DATABASE_URL
```json
"env": [
  "DATABASE_URL=postgresql://heramb:Heramb2023@db_solar_database:2700/db_solar",
  "SECRET_KEY=your-secret-key-here-change-this",
  "ALLOWED_HOSTS=db-solar.co.in,www.db-solar.co.in,72.60.98.248,db-solar-webapp.fhibgf.easypanel.host",
  "DEBUG=False"
]
```

### Domain Configuration - Corrected Port
```json
"domains": [
  {
    "host": "db-solar-webapp.fhibgf.easypanel.host",
    "https": true,
    "port": 8000,  // Changed from 80 to 8000
    "path": "/",
    "middlewares": [],
    "certificateResolver": "letsencrypt",
    "wildcard": false,
    "internalProtocol": "http"
  }
]
```

## Alternative: Use Individual Environment Variables

Instead of `DATABASE_URL`, you can use individual variables (which your settings.py supports):

```json
"env": [
  "DB_HOST=db_solar_database",
  "DB_PORT=2700",
  "DB_NAME=db_solar",
  "DB_USER=heramb",
  "DB_PASSWORD=Heramb2023",
  "SECRET_KEY=your-secret-key-here-change-this",
  "ALLOWED_HOSTS=db-solar.co.in,www.db-solar.co.in,72.60.98.248,db-solar-webapp.fhibgf.easypanel.host",
  "DEBUG=False"
]
```

## Important Notes

1. **Service Name Format**: In Easypanel, services are accessible via `projectName_serviceName`, so:
   - Project: `db_solar`
   - Service: `database`
   - Hostname: `db_solar_database` ✅ (Your current config is correct)

2. **Port 2700**: If your database is already running on port 2700, make sure:
   - The DATABASE_URL uses port 2700
   - The database service exposes port 2700 (if needed)

3. **Database Name**: `db_solar` ✅ (Correct)

4. **Username**: `heramb` ✅ (Matches your settings.py default)

5. **Password**: `Heramb2023` ✅ (Matches your settings.py default)

## Verification Steps

After updating the configuration:

1. **Check Database Connection**:
   - Look for "Database connection successful!" in container logs
   - Verify no connection errors

2. **Check Static Files**:
   - Verify logos/images are loading
   - Check browser console for 404 errors on static files

3. **Check Domain**:
   - Verify domain points to correct port (8000)
   - Test HTTPS certificate

4. **Check Environment Variables**:
   - Verify all env vars are set correctly
   - Check SECRET_KEY is set (not default)

## Quick Fix Summary

**Minimum changes needed:**
1. Change `DATABASE_URL` port from `5432` to `2700`
2. Change domain port from `80` to `8000`
3. Add `SECRET_KEY` environment variable
4. Add `ALLOWED_HOSTS` environment variable
5. Change `postgres://` to `postgresql://` in DATABASE_URL
