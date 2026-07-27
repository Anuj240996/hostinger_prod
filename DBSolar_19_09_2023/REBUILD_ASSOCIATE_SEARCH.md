# Associate Staff search — deploy checklist

Code is on GitHub branch **`version-3`** (commit with `Associate Staff` radio + filters).

## Verify live server (before rebuild)

Open: `https://app.db-solar.co.in/api/v1/status/`

| Server state | What you see | Action |
|--------------|--------------|--------|
| **OLD (current)** | Only `ok`, `architecture`, `auth` — **no** `associate`, `consumer`, or `web` keys | Rebuild required |
| **NEW (after rebuild)** | Includes `"web": { "search_associate_staff": true, "build": "search-associate-v3-20260327" }` | Search page will show 3 radios |

## EasyPanel — db-solar-v2

1. **Source** → GitHub `Anuj240996/hostinger_prod`
2. **Branch** → `version-3` (not `version-2`)
3. **Root / build directory** → `DBSolar_19_09_2023`
4. Click **Rebuild** (enable **clear build cache** if available)
5. Wait until status is **Running** and logs show `Starting Gunicorn on 0.0.0.0:8000`
6. Hard refresh search page: `https://app.db-solar.co.in/customer/search_by_staff` (Ctrl+F5)

## After rebuild — search page

Same row, three options:

- Search by Staff
- Search by Consumer
- **Associate Staff**

Select **Associate Staff** → choose associate / days / status → **Search** → table shows **Assign Associate** column.
