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

# Collect static files
echo "Collecting static files..."
echo "Checking source directories..."
ls -la /app/static/images/ 2>/dev/null | head -5 || echo "static/images not found"
ls -la /app/asert/images/ 2>/dev/null | head -5 || echo "asert/images not found"

python manage.py collectstatic --noinput --clear || {
    echo "Warning: Static files collection failed, but continuing..."
}

echo "Static files collection completed. Checking staticfiles directory..."
ls -la /app/staticfiles/images/ 2>/dev/null | head -10 || echo "staticfiles/images directory not found or empty"
echo "Total files in staticfiles:"
find /app/staticfiles -type f | wc -l || echo "0"

# Execute the command
echo "Starting application..."
exec "$@"
