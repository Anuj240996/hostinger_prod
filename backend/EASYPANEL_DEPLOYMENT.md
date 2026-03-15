# Easypanel Deployment Guide

This guide explains how to deploy the DB Solar Backend API on Hostinger Easypanel.

## Prerequisites

- Easypanel account with Postgres service
- Docker support enabled

## Environment Variables

The following environment variables need to be configured in Easypanel:

### Required Variables

- **DATABASE_URL**: Automatically provided by Easypanel Postgres service
  - Format: `postgresql://username:password@host:port/database`
  - This is automatically injected by Easypanel when you link the Postgres service

- **JWT_SECRET**: Secret key for JWT token signing
  - Generate a strong random string: `openssl rand -base64 32`
  - Example: `your-super-secret-jwt-key-here`

### Optional Variables

- **PORT**: Port number for the application (default: 8080)
  - Easypanel typically sets this automatically

- **NODE_ENV**: Environment mode (default: `production` in Docker)
  - Set to `production` for production deployments

- **JWT_EXPIRES_IN**: JWT token expiration time (default: `7d`)
  - Examples: `1h`, `24h`, `7d`, `30d`

## Deployment Steps

### 1. Create Postgres Service in Easypanel

1. In your Easypanel project, add a Postgres service
2. Note the service name (e.g., `postgres`)

### 2. Create App Service

1. Add a new App service in Easypanel
2. Connect it to your Git repository
3. Set the build context to the `backend` directory (or root if Dockerfile is in root)
4. Link the Postgres service to your App service
   - This automatically provides `DATABASE_URL` environment variable

### 3. Configure Environment Variables

In your App service settings, add the following environment variables:

```
JWT_SECRET=your-generated-secret-key-here
NODE_ENV=production
PORT=8080
```

**Note**: `DATABASE_URL` is automatically provided by Easypanel when you link the Postgres service. You don't need to set it manually.

### 4. Build and Deploy

1. Easypanel will automatically build the Docker image using the Dockerfile
2. The application will start and connect to the Postgres database using `DATABASE_URL`
3. Check the logs to ensure the application started successfully

### 5. Run Database Migrations (if needed)

If you need to run database migrations, you can:

1. Access the container shell via Easypanel
2. Run: `npm run migrate`
3. Or create a one-time job in Easypanel to run migrations

## Health Check

The application includes a health check endpoint at `/api/health` that Easypanel can use to monitor the service.

## File Uploads

The application stores uploaded files in the `uploads/` directory. Consider:

1. Using Easypanel volumes to persist uploads
2. Or configuring cloud storage (S3, etc.) for production

## Troubleshooting

### Database Connection Issues

- Verify that the Postgres service is linked to your App service
- Check that `DATABASE_URL` is set in environment variables
- Review application logs for connection errors

### SSL Connection Errors

The application automatically handles SSL for remote databases. If you encounter SSL errors:
- Verify the `DATABASE_URL` format is correct
- Check that the Postgres service allows connections from your app

### Port Issues

- Ensure the `PORT` environment variable matches Easypanel's port configuration
- The Dockerfile exposes port 8080 by default

## Docker Image Details

- Base Image: `node:18-alpine` (lightweight Alpine Linux)
- Multi-stage build for optimized image size
- Runs as non-root user (`nodejs`) for security
- Includes health check endpoint

## Support

For issues specific to:
- **Easypanel**: Check Easypanel documentation
- **Application**: See `README.md` and `API_DOCUMENTATION.md`
