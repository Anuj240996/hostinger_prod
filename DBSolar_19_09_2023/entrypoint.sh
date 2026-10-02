#!/bin/sh
# EasyPanel entrypoint — always starts Gunicorn (never crash-loops on migrate/DB wait).
# Version stamp appears in logs so you can confirm the new image is running.

echo "=== entrypoint auto-v4 (always-start gunicorn) ==="
echo "Starting application setup..."
echo "Architecture: Option A — Django owns this database; phone app must use HTTP APIs (not direct DB)."

# DATABASE_URL is required for a healthy app, but do not abort before Gunicorn
# (empty EasyPanel logs / yellow status are worse than a running unhealthy app).
if [ -z "${DATABASE_URL:-}" ]; then
  echo "WARNING: DATABASE_URL is not set."
  echo "Example: postgres://USER:PASS@database:5432/db_solar_v2"
  echo "Host must be the EasyPanel Postgres service name (usually: database)."
  echo "Continuing startup so container logs stay visible..."
fi

# Show DB host without password (helps debug Bad Gateway / No route to host)
python - <<'PY' || true
import os, re, sys
url = os.environ.get("DATABASE_URL", "")
if not url:
    print("DATABASE_URL empty — skip host parse.")
    sys.exit(0)
m = re.match(r"^[^:]+://([^:/@]+)(?::[^@]*)?@([^:/]+)(?::(\d+))?/(.+)$", url)
if not m:
    print("WARNING: DATABASE_URL format looks invalid.")
    print("Expected: postgres://USER:PASS@HOST:5432/DBNAME")
    sys.exit(0)
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

# Wait for database to be ready (do not exit — always reach Gunicorn)
echo "Waiting for database..."
MAX_ATTEMPTS=20
ATTEMPT=0
DB_OK=0

if [ -n "${DATABASE_URL:-}" ]; then
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
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
"; then
      echo "Database is up - proceeding with setup"
      DB_OK=1
      break
    else
      ATTEMPT=$((ATTEMPT + 1))
      echo "Database is unavailable - sleeping (attempt $ATTEMPT/$MAX_ATTEMPTS)"
      sleep 2
    fi
  done
fi

if [ "$DB_OK" -ne 1 ]; then
  echo "WARNING: Database not reachable after wait — starting Gunicorn anyway."
  echo "Fix DATABASE_URL host (usually 'database'), then Redeploy."
fi

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

# ---- migrations: never abort container (set +e) ----
set +e
echo "Running database migrations (fully automatic safe mode)..."
if [ -f /app/fix_startup_migrations.py ]; then
  python /app/fix_startup_migrations.py
  MIG_RC=$?
else
  echo "fix_startup_migrations.py missing — falling back to migrate --fake-initial"
  python manage.py migrate --noinput --fake-initial
  MIG_RC=$?
fi
if [ "$MIG_RC" -ne 0 ]; then
  echo "WARNING: migration helper exit code=$MIG_RC — starting app anyway."
fi
set -e
# ---- end migrations ----

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
# Always start this app. Ignore EasyPanel custom CMD that can point at a broken WSGI path.
exec gunicorn --chdir /app --bind 0.0.0.0:8000 --workers "${WEB_CONCURRENCY:-1}" --timeout 120 --access-logfile - --error-logfile - gunicorn_wsgi:application
