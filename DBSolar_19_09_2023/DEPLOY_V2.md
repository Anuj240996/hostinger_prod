# DB Solar — Version 2 deployment (EasyPanel / Hostinger VPS)

This folder is the **deploy copy**. The original offline project (`DBSolar_19_09_2023`) is unchanged.

## What was configured

- `Dockerfile`, `entrypoint.sh`, `docker-compose.yml`, `.dockerignore` — from production `rollback-version`
- `requirements.txt` — production pins + `crispy-bootstrap4==2024.1`, `django-formtools==2.3`, `dj-database-url==2.1.0`
- `inventoryproject/settings.py` — env-based config, CRM apps, `formtools`, `Asia/Kolkata`

## Git — push to `hostinger_prod` (branch `version-2`)

Run from a machine with network access to GitHub (VPS recommended if Windows checkout fails).

```bash
# 1) Clone production repo (shallow)
git clone --depth 1 --branch rollback-version https://github.com/Anuj240996/hostinger_prod.git
cd hostinger_prod

# 2) Create Version 2 branch (does not touch rollback-version)
git checkout -b version-2

# 3) Replace app folder with this deploy copy
#    (adjust source path to where you uploaded DBSolar_19_09_2023_v2_deploy)
rm -rf DBSolar_19_09_2023
cp -r /path/to/DBSolar_19_09_2023_v2_deploy DBSolar_19_09_2023

# 4) Commit and push
git add DBSolar_19_09_2023
git status
git commit -m "Deploy Version 2: CRM merge, Docker, production-safe requirements"
git push -u origin version-2
```

**Do not** push to `rollback-version`, `main`, or `master`.

## EasyPanel — new service (keep V1 running)

1. **Add new app** (e.g. `db-solar-v2`) — do not modify the existing V1 app.
2. **Source:** GitHub `Anuj240996/hostinger_prod`, branch **`version-3`** (use `version-3` for Option A + associate search; `version-2` is older).
3. **Build context / root:** `DBSolar_19_09_2023` (folder containing `Dockerfile`).
4. **Build:** Dockerfile (auto-detected).
5. **Port:** `8000` (internal). EasyPanel “HTTP port” / target port must be **8000**, not 80.
6. **Domain:** new subdomain (e.g. `v2.db-solar.co.in`) or EasyPanel `*.easypanel.host` URL.

### Site shows “Service is not reachable”

EasyPanel’s proxy cannot connect to Gunicorn. Check in order:

1. **Service logs** — look for `=== Starting Gunicorn on 0.0.0.0:8000 ===`. If logs stop at `collectstatic`, redeploy after pulling latest `version-2` (static files are collected at **build** time now).
2. **Port** — app listens on **8000** (`Dockerfile` / `CMD` gunicorn bind).
3. **Container status** — not crash-looping (OOM during old `collectstatic --clear` was a common cause).
4. **`ALLOWED_HOSTS`** — must include your hostname, e.g. `db-solar-db-solar-v2.fhibgf.easypanel.host` or `.easypanel.host` (default in settings includes `.easypanel.host`).
5. **`CSRF_TRUSTED_ORIGINS`** (optional): full URLs only, e.g. `https://db-solar-db-solar-v2.fhibgf.easypanel.host` — or omit and settings will add `https://` from `ALLOWED_HOSTS`. Do **not** copy `ALLOWED_HOSTS` verbatim (no `.easypanel.host` wildcards).
6. **Rebuild** the image after git push (not only restart) so Dockerfile `collectstatic` runs.

### Environment variables (V2 / version-3 service)

| Variable | Example / notes |
|----------|-----------------|
| `DATABASE_URL` | `postgres://USER:PASS@database:5432/db_solar_v2` — host must be EasyPanel Postgres service name (**`database`**, not `db_solar_database`) |
| `SECRET_KEY` | New random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `app.db-solar.co.in,db-solar-db-solar-v2.fhibgf.easypanel.host,.easypanel.host,72.60.98.248,localhost` |
| `VPS_PUBLIC_IP` | `72.60.98.248` (optional; adds IP to `ALLOWED_HOSTS`) |
| `WEB_CONCURRENCY` | `1` (default; use `2` only if RAM allows) |
| `CSRF_TRUSTED_ORIGINS` | **Leave unset** (or `https://app.db-solar.co.in` only) |
| `EMAIL_*` | Same pattern as V1 if email is required |

**Do not set** `CSRF_TRUSTED_ORIGINS` to the same value as `ALLOWED_HOSTS`.

`entrypoint.sh` requires **`DATABASE_URL`** (not only `DB_*`).

### Option A (phone + web share data)

- **Django owns** `db_solar_v2` and runs all migrations.
- **Phone app must NOT** set `DATABASE_URL` to this database.
- Phone app calls HTTPS APIs under `/api/` (status: `/api/v1/status/`).
- Bring **web** up first; change phone app only after web is stable.

### Health check (fixes “domain correct but page never loads”)

In **db-solar-v2** → **Advanced / Health check** (if available):

- **Path:** `/health/`
- **Port:** `8000`
- **Expected:** HTTP `200` with body `ok`

If the probe hits `/` and gets `400 Disallowed Host`, EasyPanel marks the service down even though Gunicorn is running.

### Same server IP as V1 (`72.60.98.248:8000`)

V1 and V2 **cannot both use host port 8000**. Use two ports:

| App | Host URL (example) | EasyPanel “Publish port” |
|-----|------------------|-------------------------|
| V1 (production) | `http://72.60.98.248:8000` | `8000` → container `8000` |
| V2 (testing) | `http://72.60.98.248:8001` | `8001` → container `8000` |

Steps for V2:

1. **db-solar-v2** → **Ports** → add **public** mapping `8001` → `8000`.
2. Env: `ALLOWED_HOSTS=72.60.98.248,db-solar-db-solar-v2.fhibgf.easypanel.host,.easypanel.host,localhost`  
   Or set `VPS_PUBLIC_IP=72.60.98.248`.
3. Open **`http://72.60.98.248:8001/`** (login page).

HTTPS EasyPanel URL still works in parallel:  
`https://db-solar-db-solar-v2.fhibgf.easypanel.host/`

### “Same website” as production (`db-solar.co.in`)

You **cannot** run V1 and V2 on the **same URL + same database** without replacing production.

Safe options:

1. **Subdomain (recommended):** `v2.db-solar.co.in` → DNS A record to `72.60.98.248` → add domain on **db-solar-v2** only. V1 stays on `www.db-solar.co.in`.
2. **Same IP, different port:** `http://72.60.98.248:8001` (above).
3. **Same domain, path `/v2/`:** requires reverse-proxy rules in EasyPanel **and** env `FORCE_SCRIPT_NAME=/v2` on V2 (advanced; test carefully).

### High memory (~80%), low CPU (0%)

- Normal if **no browser traffic** reaches the app (CPU idle).
- This image is large (OpenCV, etc.). Default **`WEB_CONCURRENCY=1`** keeps one Gunicorn worker.
- Ensure only **one** V2 replica in EasyPanel if memory is tight.
- After opening the site, you should see `GET /` lines in logs and CPU may rise slightly.

### Database

- Create a **separate** PostgreSQL database for V2 (`solar_db_v2`).
- Run migrations on first deploy (entrypoint runs `migrate` automatically).
- Do not point V2 at the live V1 database until you have a migration/backup plan.

## Local smoke test (optional)

```bash
cd DBSolar_19_09_2023_v2_deploy
cp .env.example .env
# Edit .env — set DATABASE_URL for the db service
docker compose up --build
```

Open `http://localhost:8000` (compose maps port 8000).

## Rollback

- **V1:** unchanged on `rollback-version` and current EasyPanel service.
- **V2:** delete or stop the V2 EasyPanel app; switch DNS back to V1.
