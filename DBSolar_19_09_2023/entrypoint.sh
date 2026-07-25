#!/bin/bash
set -e

echo "Starting application setup..."
echo "Architecture: Option A — Django owns this database; phone app must use HTTP APIs (not direct DB)."

# Require DATABASE_URL (EasyPanel must set this)
if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set."
  echo "Example: postgres://USER:PASS@database:5432/db_solar_v2"
  echo "Host must be the EasyPanel Postgres service name (usually: database)."
  exit 1
fi

# Show DB host without password (helps debug Bad Gateway / No route to host)
python - <<'PY'
import os, re, sys
url = os.environ.get("DATABASE_URL", "")
# postgres://user:pass@host:5432/db
m = re.match(r"^[^:]+://([^:/@]+)(?::[^@]*)?@([^:/]+)(?::(\d+))?/(.+)$", url)
if not m:
    print("ERROR: DATABASE_URL format is invalid.")
    print("Expected: postgres://USER:PASS@HOST:5432/DBNAME")
    sys.exit(1)
user, host, port, db = m.group(1), m.group(2), m.group(3) or "5432", m.group(4)
print(f"DATABASE_URL target: user={user} host={host} port={port} db={db}")
stale = {"db_solar_database", "db-solar-database"}
if host in stale or host.startswith("10."):
    print("=" * 60)
    print(f"WARNING: DB host '{host}' looks stale / unreachable on EasyPanel.")
    print("Set DATABASE_URL host to the Postgres service name, usually: database")
    print("Example: postgres://heramb:PASSWORD@database:5432/db_solar_v2")
    print("=" * 60)
PY

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
"; then
    echo "Database is up - proceeding with setup"
    break
  else
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
      echo "ERROR: Could not connect to database after $MAX_ATTEMPTS attempts."
      echo "Fix DATABASE_URL host (use EasyPanel service name 'database'), then Redeploy."
      exit 1
    fi
    echo "Database is unavailable - sleeping (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
  fi
done

mkdir -p /app/media/profile_pics
if [ ! -f /app/media/profile_pics/default.png ]; then
  if [ -f /app/media/profile_images/default.png ]; then
    cp /app/media/profile_images/default.png /app/media/profile_pics/default.png
    echo "Copied default profile image to media/profile_pics/default.png"
  elif [ -f /app/static/images/dblogosmall.png ]; then
    cp /app/static/images/dblogosmall.png /app/media/profile_pics/default.png
    echo "Created default profile image at media/profile_pics/default.png"
  elif [ -f /app/staticfiles/images/dblogosmall.png ]; then
    cp /app/staticfiles/images/dblogosmall.png /app/media/profile_pics/default.png
    echo "Created default profile image at media/profile_pics/default.png from staticfiles"
  fi
fi

if [ "${SKIP_MIGRATE:-0}" = "1" ]; then
  echo "SKIP_MIGRATE=1 — skipping migrations."
else
  echo "Running database migrations..."
  python manage.py migrate --noinput || {
      echo "ERROR: Database migrations failed. The app will not start until migrations succeed."
      echo "For a fresh V2 database (db_solar_v2), drop and recreate the database, then redeploy."
      exit 1
  }
fi

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
echo "Health probe: GET /health/  (internal check: curl -s http://127.0.0.1:8000/health/)"
echo "Proxy must point to this service on port 8000."
exec "$@"
