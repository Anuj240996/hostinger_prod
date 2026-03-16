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
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', ''),
        dbname=os.environ.get('DB_NAME', 'postgres'),
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

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "Warning: Migrations failed, but continuing..."
}

# Verify static file directories exist and contain files
echo "=== Verifying static file directories ==="
echo "Checking /app/static/images/:"
ls -la /app/static/images/dblogo*.png 2>/dev/null | head -3 || echo "No logo files in static/images"
echo "Checking /app/asert/images/:"
ls -la /app/asert/images/dblogo*.png 2>/dev/null | head -3 || echo "No logo files in asert/images"
echo "Checking /app/media/:"
ls -la /app/media/ 2>/dev/null | head -3 || echo "Media directory empty or not found"
echo "Static files will be served directly from source directories (no collectstatic needed)"

# Execute the command
echo "Starting application..."
exec "$@"
