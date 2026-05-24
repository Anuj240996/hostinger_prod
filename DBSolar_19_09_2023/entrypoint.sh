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
        dsn=os.environ.get('DATABASE_URL'),
        connect_timeout=5,
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

mkdir -p /app/media/profile_images
if [ ! -f /app/media/profile_images/default.png ]; then
  if [ -f /app/static/images/dblogosmall.png ]; then
    cp /app/static/images/dblogosmall.png /app/media/profile_images/default.png
    echo "Created default profile image at media/profile_images/default.png"
  fi
fi

echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "ERROR: Database migrations failed. The app will not start until migrations succeed."
    echo "For a fresh V2 database (db_solar_v2), drop and recreate the database, then redeploy."
    exit 1
}

# collectstatic runs at Docker build time. Re-run only when forced (e.g. after static changes).
if [ "${RUN_COLLECTSTATIC:-0}" = "1" ]; then
  echo "RUN_COLLECTSTATIC=1 — collecting static files..."
  python manage.py collectstatic --noinput || echo "Warning: collectstatic failed, continuing..."
elif [ ! -f /app/staticfiles/admin/css/base.css ]; then
  echo "Static files missing — running collectstatic (no --clear)..."
  python manage.py collectstatic --noinput || echo "Warning: collectstatic failed, continuing..."
else
  echo "Static files present — skipping collectstatic (set RUN_COLLECTSTATIC=1 to force)."
fi

echo "=== Starting Gunicorn on 0.0.0.0:8000 (workers=${WEB_CONCURRENCY:-1}) ==="
echo "Health probe: GET /health/ (configure EasyPanel health check to this path)"
exec "$@"
