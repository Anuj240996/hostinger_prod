#!/bin/sh
# EasyPanel entrypoint auto-v7 — start Gunicorn fast; never leave service unreachable.
set +e
echo "=== entrypoint auto-v7 (always-start gunicorn) ==="
echo "Starting application setup..."

if [ -z "${DATABASE_URL:-}" ]; then
  echo "WARNING: DATABASE_URL is not set. Example host: database"
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
    sys.exit(0)
user, host, port, db = m.group(1), m.group(2), m.group(3) or "5432", m.group(4)
print("DATABASE_URL target: user=%s host=%s port=%s db=%s" % (user, host, port, db))
PY

# Short wait only — do not block Gunicorn for long (EasyPanel marks unreachable)
echo "Waiting for database (max ~20s)..."
MAX_ATTEMPTS=10
ATTEMPT=0
DB_OK=0
if [ -n "${DATABASE_URL:-}" ]; then
  while [ "$ATTEMPT" -lt "$MAX_ATTEMPTS" ]; do
    if python -c "
import sys, os
try:
    import psycopg2
    conn = psycopg2.connect(dsn=os.environ.get('DATABASE_URL'), connect_timeout=3)
    conn.close()
    print('Database connection successful!')
    sys.exit(0)
except Exception as e:
    print('Database connection failed: %s' % e)
    sys.exit(1)
"; then
      DB_OK=1
      break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "Database unavailable - sleep (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
  done
fi
if [ "$DB_OK" -ne 1 ]; then
  echo "WARNING: Database not ready — starting Gunicorn anyway."
fi

mkdir -p /app/media/profile_pics 2>/dev/null || true

echo "Running migrations (non-blocking on failure)..."
if [ -f /app/fix_startup_migrations.py ]; then
  python /app/fix_startup_migrations.py || echo "WARNING: migration helper failed - continuing"
else
  python manage.py migrate --noinput --fake-initial || echo "WARNING: migrate failed - continuing"
fi

echo "=== Starting Gunicorn on 0.0.0.0:8000 (workers=${WEB_CONCURRENCY:-1}) ==="
if [ -f /app/gunicorn_wsgi.py ]; then
  WSGI_APP="gunicorn_wsgi:application"
elif [ -f /app/inventoryproject/wsgi.py ]; then
  WSGI_APP="inventoryproject.wsgi:application"
else
  echo "ERROR: No WSGI module. Sleeping so logs stay visible."
  sleep 3600
  exit 1
fi
echo "WSGI: $WSGI_APP"
echo "Health: http://0.0.0.0:8000/health/"
# Keep process in foreground so EasyPanel sees a running service
exec gunicorn --chdir /app --bind 0.0.0.0:8000 --workers "${WEB_CONCURRENCY:-1}" --timeout 120 --access-logfile - --error-logfile - "$WSGI_APP"
