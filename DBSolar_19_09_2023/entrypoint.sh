#!/bin/sh
# EasyPanel entrypoint - ALWAYS start Gunicorn (never crash-loop / empty logs).
# Look for this stamp in EasyPanel Logs after Deploy:
#   === entrypoint auto-v6 (always-start gunicorn) ===

set +e
echo "=== entrypoint auto-v6 (always-start gunicorn) ==="
echo "Starting application setup..."

if [ -z "${DATABASE_URL:-}" ]; then
  echo "WARNING: DATABASE_URL is not set."
  echo "Example: postgres://USER:PASS@database:5432/db_solar_v2"
  echo "Host must be the EasyPanel Postgres service name (usually: database)."
  echo "Continuing startup so container logs stay visible..."
fi

python - <<'PY' || true
import os, re, sys
url = os.environ.get("DATABASE_URL", "")
if not url:
    print("DATABASE_URL empty - skip host parse.")
    sys.exit(0)
m = re.match(r"^[^:]+://([^:/@]+)(?::[^@]*)?@([^:/]+)(?::(\d+))?/(.+)$", url)
if not m:
    print("WARNING: DATABASE_URL format looks invalid.")
    print("Expected: postgres://USER:PASS@HOST:5432/DBNAME")
    sys.exit(0)
user, host, port, db = m.group(1), m.group(2), m.group(3) or "5432", m.group(4)
print("DATABASE_URL target: user=%s host=%s port=%s db=%s" % (user, host, port, db))
stale = {"db_solar_database", "db-solar-database"}
if host in stale or host.startswith("10."):
    print("WARNING: DB host '%s' looks stale. Use host 'database'." % host)
PY

echo "Waiting for database..."
MAX_ATTEMPTS=15
ATTEMPT=0
DB_OK=0

if [ -n "${DATABASE_URL:-}" ]; then
  while [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; do
    if python -c "
import sys, os
try:
    import psycopg2
    conn = psycopg2.connect(dsn=os.environ.get('DATABASE_URL'), connect_timeout=5)
    conn.close()
    print('Database connection successful!')
    sys.exit(0)
except Exception as e:
    print('Database connection failed: %s' % e)
    sys.exit(1)
"; then
      echo "Database is up - proceeding with setup"
      DB_OK=1
      break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "Database unavailable - sleep (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
  done
fi

if [ "$DB_OK" -ne 1 ]; then
  echo "WARNING: Database not reachable - starting Gunicorn anyway."
fi

mkdir -p /app/media/profile_pics 2>/dev/null || true

echo "Running database migrations (safe mode)..."
if [ -f /app/fix_startup_migrations.py ]; then
  python /app/fix_startup_migrations.py || echo "WARNING: migration helper failed - continuing"
else
  python manage.py migrate --noinput --fake-initial || echo "WARNING: migrate failed - continuing"
fi

if [ "${RUN_COLLECTSTATIC:-0}" = "1" ] || [ ! -f /app/staticfiles/admin/css/base.css ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput || echo "WARNING: collectstatic failed - continuing"
else
  echo "Static files present - skip collectstatic"
fi

echo "=== Starting Gunicorn on 0.0.0.0:8000 (workers=${WEB_CONCURRENCY:-1}) ==="

if [ -f /app/gunicorn_wsgi.py ]; then
  WSGI_APP="gunicorn_wsgi:application"
elif [ -f /app/inventoryproject/wsgi.py ]; then
  WSGI_APP="inventoryproject.wsgi:application"
else
  echo "ERROR: No WSGI module found. Sleeping 1h so logs stay visible."
  sleep 3600
  exit 1
fi

echo "WSGI: $WSGI_APP"
exec gunicorn --chdir /app --bind 0.0.0.0:8000 --workers "${WEB_CONCURRENCY:-1}" --timeout 120 --access-logfile - --error-logfile - "$WSGI_APP"
