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
2. **Source:** GitHub `Anuj240996/hostinger_prod`, branch **`version-2`**.
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

### Environment variables (V2 service)

| Variable | Example / notes |
|----------|-----------------|
| `DATABASE_URL` | `postgres://USER:PASS@HOST:5432/solar_db_v2` — **use a new database** |
| `SECRET_KEY` | New random string (not the same as V1 unless intentional) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `v2.db-solar.co.in,www.db-solar.co.in` (your V2 hostnames) |
| `EMAIL_*` | Same pattern as V1 if email is required |

`entrypoint.sh` requires **`DATABASE_URL`** (not only `DB_*`).

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
