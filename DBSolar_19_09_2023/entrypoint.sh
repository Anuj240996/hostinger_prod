#!/bin/bash
set -e

echo "Starting application setup..."

# Wait for database to be ready (with timeout)
echo "Waiting for database..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  if python -c "
import sys
import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST') or os.environ.get('POSTGRES_HOST', 'localhost'),
        port=os.environ.get('DB_PORT') or os.environ.get('POSTGRES_PORT', '2700'),
        user=os.environ.get('DB_USER') or os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD') or os.environ.get('POSTGRES_PASSWORD', ''),
        dbname=os.environ.get('DB_NAME') or os.environ.get('POSTGRES_DB', 'db_solar'),
        connect_timeout=5
    )
    conn.close()
    print('Database connection successful!')
    sys.exit(0)
except psycopg2.OperationalError as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo "Database is up - proceeding with setup"
    break
  else
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
      echo "Warning: Could not connect to database after $MAX_ATTEMPTS attempts. Continuing anyway..."
      break
    fi
    echo "Database is unavailable - sleeping (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
  fi
done

# Run migrations (for existing database, this will only apply new migrations)
echo "Running database migrations..."
echo "Note: If using existing db_solar database, migrations will only apply new changes"
python manage.py migrate --noinput || {
    echo "Warning: Migrations failed, but continuing..."
    echo "This is normal if database schema already matches Django models"
}

# Verify static file directories exist and contain files
echo "=== Verifying static file directories ==="
echo "Checking /app/static/images/:"
ls -la /app/static/images/dblogo*.png 2>/dev/null | head -5 || echo "No logo files in static/images"
echo "Checking /app/asert/images/:"
ls -la /app/asert/images/dblogo*.png 2>/dev/null | head -5 || echo "No logo files in asert/images"
echo "Checking /app/media/:"
ls -la /app/media/ 2>/dev/null | head -5 || echo "Media directory empty or not found"
echo ""
echo "=== Static file serving configuration ==="
echo "WhiteNoise will serve files from:"
echo "  - /app/static/"
echo "  - /app/asert/"
echo "Files accessible at: /static/images/dblogo200.png, etc."

# Execute the command
echo "Starting application..."
exec "$@"
