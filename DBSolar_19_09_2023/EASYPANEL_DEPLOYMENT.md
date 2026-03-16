# Easypanel Deployment Guide

This guide will help you deploy the DBSolar Django application to Easypanel.

## Prerequisites

- Easypanel account
- PostgreSQL database (can be provisioned through Easypanel)
- Domain name (optional, for custom domain)

## Deployment Steps

### 1. Prepare Your Repository

Ensure your code is pushed to a Git repository (GitHub, GitLab, etc.) that Easypanel can access.

### 2. Create a New App in Easypanel

1. Log in to your Easypanel dashboard
2. Click "New App" or "Create App"
3. Select "Docker" or "Custom" deployment type

### 3. Configure the App

#### Build Settings:
- **Build Method**: Dockerfile
- **Dockerfile Path**: `Dockerfile` (root of repository)
- **Context**: Root directory

#### Environment Variables:

Set the following environment variables in Easypanel:

**Required:**
```
DB_HOST=<your-postgres-host>
DB_PORT=2700
DB_NAME=db_solar
DB_USER=<your-db-user>
DB_PASSWORD=<your-db-password>
SECRET_KEY=<generate-a-secure-secret-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DEBUG=False
```

**Note:** If using Easypanel's PostgreSQL service, you can also use:
```
POSTGRES_HOST=<service-name>
POSTGRES_PORT=2700
POSTGRES_DB=db_solar
POSTGRES_USER=<your-db-user>
POSTGRES_PASSWORD=<your-db-password>
```

**Optional (for email functionality):**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Port Configuration:
- **Container Port**: `8000`
- **Public Port**: `8000` (or configure through Easypanel's reverse proxy)

### 4. Database Setup

#### Option A: Use Easypanel's PostgreSQL Service
1. Create a PostgreSQL database service in Easypanel
2. Use the connection details provided by Easypanel for your environment variables

#### Option B: External PostgreSQL Database
1. Use your existing PostgreSQL database
2. Ensure the database is accessible from Easypanel's network
3. Update `DB_HOST` with the external database host

### 5. Storage Volumes (Optional)

If you need persistent storage for media files:

1. In Easypanel, add a volume mount:
   - **Host Path**: `/app/media` (or your preferred path)
   - **Container Path**: `/app/media`

2. For static files, they are collected during container startup and can be served via Django or a CDN.

### 6. Deploy

1. Click "Deploy" or "Save" in Easypanel
2. Monitor the build logs
3. Once deployed, the application will:
   - Wait for database connection
   - Run migrations automatically
   - Collect static files
   - Start the Gunicorn server

### 7. Post-Deployment

#### Initial Setup:
1. Access your application URL
2. Create a superuser (if needed):
   ```bash
   # In Easypanel's terminal/exec:
   python manage.py createsuperuser
   ```

#### Health Check:
- The application should be accessible at your configured domain/URL
- Check logs in Easypanel for any errors

## Configuration Details

### Gunicorn Settings

The application runs with Gunicorn with the following defaults:
- **Workers**: 3
- **Timeout**: 120 seconds
- **Bind**: 0.0.0.0:8000
- **Logs**: stdout/stderr

To customize, you can override the CMD in Easypanel or modify the Dockerfile.

### Static Files

Static files are collected during container startup. For production, consider:
1. Using a CDN (CloudFlare, AWS CloudFront, etc.)
2. Serving static files via Nginx (configure in Easypanel)
3. Using Django's static file serving (only for development)

### Media Files

Media files are stored in `/app/media`. Ensure this directory is:
1. Mounted as a volume for persistence
2. Backed up regularly
3. Has appropriate permissions

## Troubleshooting

### Database Connection Issues
- Verify environment variables are set correctly
- Check database firewall/network settings
- Ensure database is accessible from Easypanel's network

### Migration Errors
- Check database permissions
- Review migration files
- Run migrations manually if needed: `python manage.py migrate`

### Static Files Not Loading
- Verify `STATIC_ROOT` setting in `settings.py`
- Check file permissions
- Ensure static files are collected: `python manage.py collectstatic`

### Application Not Starting
- Check container logs in Easypanel
- Verify all environment variables are set
- Ensure port 8000 is exposed and accessible

## Security Recommendations

1. **Never commit secrets**: Use environment variables for all sensitive data
2. **Update SECRET_KEY**: Generate a new secret key for production
3. **Set DEBUG=False**: Always disable debug mode in production
4. **Configure ALLOWED_HOSTS**: Set to your actual domain(s)
5. **Use HTTPS**: Configure SSL/TLS through Easypanel or a reverse proxy
6. **Database Security**: Use strong passwords and restrict database access

## Monitoring

- Monitor application logs in Easypanel dashboard
- Set up health checks if available
- Monitor database connections and performance
- Track application metrics (CPU, memory, requests)

## Updates and Maintenance

1. **Code Updates**: Push to your repository, Easypanel will rebuild automatically (if configured)
2. **Database Migrations**: Run automatically on container startup
3. **Static Files**: Collected automatically on container startup
4. **Dependencies**: Update `requirements.txt` and redeploy

## Support

For issues specific to:
- **Easypanel**: Check Easypanel documentation and support
- **Django Application**: Review application logs and Django documentation
- **Database**: Check PostgreSQL logs and connection settings
