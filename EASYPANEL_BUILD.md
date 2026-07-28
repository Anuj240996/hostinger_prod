# EasyPanel db-solar-v2 — build path

Live app: https://app.db-solar.co.in  
EasyPanel: http://72.60.98.248:3000/projects/db_solar/app/db-solar-v2

## Correct mapping

| Place | Path |
|-------|------|
| GitHub repo | `Anuj240996/hostinger_prod` |
| Branch | `version-3` |
| Django app (code) | `DBSolar_19_09_2023/` |
| Local working copy (same files) | `DBSolar_19_09_2023_v2_deploy/` |

Local `DBSolar_19_09_2023_v2_deploy` content is what belongs **inside** GitHub folder `DBSolar_19_09_2023/`.

## EasyPanel Source settings (use one)

### Option A (recommended)

- **Branch:** `version-3`
- **Build path / context:** `DBSolar_19_09_2023`
- **Dockerfile:** `Dockerfile` (auto)

### Option B (repo root)

- **Branch:** `version-3`
- **Build path / context:** `.` or empty (repo root)
- **Dockerfile:** root `Dockerfile` (copies `DBSolar_19_09_2023/` into the image)

## After settings look correct

1. **Rebuild** (clear cache if available)
2. Wait for Gunicorn start
3. Open https://app.db-solar.co.in/customer/search_by_staff and hard refresh (Ctrl+F5)
4. You must see: **Search by Staff** · **Search by Consumer** · **Search by Associate**
