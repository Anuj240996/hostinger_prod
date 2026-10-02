# EasyPanel db-solar-v2 — build path

Live app: https://app.db-solar.co.in  
EasyPanel: http://72.60.98.248:3000/projects/db_solar/app/db-solar-v2

## Correct mapping

| Place | Path |
|-------|------|
| GitHub repo | `Anuj240996/hostinger_prod` |
| Branch | `version-3` |
| Django app (code) | `DBSolar_19_09_2023/` |

## EasyPanel Source settings (use one)

### Option A (recommended)

- **Branch:** `version-3`
- **Build path / context:** `DBSolar_19_09_2023`
- **Dockerfile:** `Dockerfile` (auto)

### Option B (repo root)

- **Branch:** `version-3`
- **Build path / context:** `.` or empty (repo root)
- **Dockerfile:** root `Dockerfile` (copies `DBSolar_19_09_2023/` into the image)

## If service is yellow, CPU/Memory 0, Logs empty

1. Open **Source** — confirm branch `version-3` and build path as above
2. Open **Environment** — `DATABASE_URL` host must be `database` (Postgres service name)
3. Open **Deployments** — if last build failed, read the error
4. Click green **Deploy** (clear build cache if available)
5. Wait until Logs show: `=== entrypoint auto-v4 (always-start gunicorn) ===`
6. Then: `=== Starting Gunicorn on 0.0.0.0:8000`
7. Hard refresh https://app.db-solar.co.in

## After settings look correct

1. **Rebuild** (clear cache if available)
2. Wait for Gunicorn start
3. Open https://app.db-solar.co.in and hard refresh (Ctrl+F5)
