"""Associate Option A services — ports phone-app associate SQL/builders with same JSON shapes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import connection


STAGE_META = [
    {"stage": "Lead", "color": 0xFF059669, "icon": "person_add"},
    {"stage": "Site Survey", "color": 0xFF2563EB, "icon": "description"},
    {"stage": "Quotation", "color": 0xFF7C3AED, "icon": "request_quote"},
    {"stage": "Approval", "color": 0xFFD97706, "icon": "fact_check"},
    {"stage": "Installation", "color": 0xFF0891B2, "icon": "handyman"},
    {"stage": "Deployed", "color": 0xFF059669, "icon": "verified"},
]


def _fetchall_dict(sql: str, params=None) -> List[Dict[str, Any]]:
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        cols = [c[0] for c in cursor.description] if cursor.description else []
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _fetchone_dict(sql: str, params=None) -> Optional[Dict[str, Any]]:
    rows = _fetchall_dict(sql, params)
    return rows[0] if rows else None


def _bit_true(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1
    s = str(value).strip().lower()
    return s in ("1", "true", "t", "yes")


def is_staff_auth_user(user: User) -> bool:
    username = (user.username or "").strip().lower()
    if username.startswith("db_"):
        return False
    if username.startswith("aso_"):
        return True
    return bool(user.is_staff)


def find_staff_user_by_login(login_id: str) -> Optional[User]:
    login_id = (login_id or "").strip()
    if not login_id:
        return None
    qs = User.objects.filter(username__iexact=login_id).first()
    if qs:
        return qs
    return User.objects.filter(email__iexact=login_id).first()


def authenticate_associate(username: str, password: str) -> Optional[User]:
    user = find_staff_user_by_login(username)
    if not user or not is_staff_auth_user(user):
        return None
    # authenticate() needs username; resolve by email if needed
    auth_user = authenticate(username=user.username, password=password)
    return auth_user if auth_user and is_staff_auth_user(auth_user) else None


def ensure_user_app_auth_user_column() -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE user_app ADD COLUMN IF NOT EXISTS auth_user_id INTEGER"
        )


def associate_display_name(name: str) -> str:
    n = (name or "").strip()
    if n.lower().startswith("aso_"):
        return n[4:].strip() or n
    return n


def resolve_associate_context(auth_user_id: int) -> Dict[str, Any]:
    """Staff session path used by associate-login JWT (source=auth_user)."""
    ensure_user_app_auth_user_column()
    user = User.objects.filter(id=auth_user_id).first()
    if not user:
        raise ValueError("Associate auth_user not found")

    display = (
        f"{user.first_name or ''} {user.last_name or ''}".strip()
        or user.username
        or "Associate"
    )
    linked = _fetchone_dict(
        "SELECT id FROM user_app WHERE auth_user_id = %s ORDER BY id LIMIT 1",
        [auth_user_id],
    )
    app_user_id = int(linked["id"]) if linked and linked.get("id") is not None else None
    return {
        "appUserId": app_user_id,
        "name": display,
        "displayName": display,
        "email": user.email,
        "phone": None,
        "authUserIds": [int(auth_user_id)],
        "authSource": "auth_user",
    }


def map_crm_stage_to_pipeline(stage) -> str:
    s = str(stage or "").lower()
    if any(x in s for x in ("new", "contacted", "qualified", "new_app", "new_enq")):
        return "Lead"
    if any(x in s for x in ("survey", "site", "visit")):
        return "Site Survey"
    if any(x in s for x in ("quote", "quot", "negotiat")):
        return "Quotation"
    if any(x in s for x in ("approv", "token", "agreement")):
        return "Approval"
    if "install" in s:
        return "Installation"
    if any(x in s for x in ("won", "deploy", "complete", "live")):
        return "Deployed"
    return "Lead"


def map_quote_status_to_pipeline(status) -> str:
    s = str(status or "").lower()
    if s in ("converted", "won"):
        return "Deployed"
    if "approv" in s:
        return "Approval"
    if any(x in s for x in ("sent", "draft", "revised", "customer")):
        return "Quotation"
    return "Quotation"


def progress_for_stage(stage: str) -> float:
    return {
        "Lead": 0.1,
        "Site Survey": 0.25,
        "Quotation": 0.4,
        "Approval": 0.55,
        "Installation": 0.7,
        "Deployed": 1.0,
    }.get(stage, 0.15)


def fetch_customer_result(customer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not customer:
        return None
    cust_id = customer.get("cust_id")
    consumer = str(customer.get("consumer") or "").strip()
    comp_name = str(customer.get("comp_name") or "").strip()
    cols = "solar_panel, inverter, net_meter, mseb, inspection_report, consumer_id_id"

    if cust_id is not None:
        try:
            row = _fetchone_dict(
                f"SELECT {cols} FROM customer_result WHERE consumer_id_id = %s "
                "ORDER BY id DESC LIMIT 1",
                [cust_id],
            )
            if row:
                return row
        except Exception:
            pass
        try:
            row = _fetchone_dict(
                f"SELECT {cols} FROM customer_result WHERE consumer_id = %s "
                "ORDER BY id DESC LIMIT 1",
                [cust_id],
            )
            if row:
                return row
        except Exception:
            pass

    for text in dict.fromkeys([t for t in (consumer, comp_name) if t]):
        try:
            row = _fetchone_dict(
                f"SELECT {cols} FROM customer_result "
                "WHERE TRIM(consumer::text) = TRIM(%s::text) "
                "ORDER BY id DESC LIMIT 1",
                [text],
            )
            if row:
                return row
        except Exception:
            pass
    return None


def compute_project_status(result: Optional[Dict[str, Any]]) -> str:
    if not result:
        return "Pending"
    if _bit_true(result.get("inspection_report")):
        return "Completed"
    if all(
        _bit_true(result.get(k))
        for k in ("solar_panel", "inverter", "net_meter", "mseb")
    ):
        return "Completed"
    return "Pending"


def load_associate_records(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    app_user_id = ctx.get("appUserId")
    auth_user_ids = list(ctx.get("authUserIds") or [])
    items: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def push(row: Dict[str, Any]) -> None:
        key = f"{row['source']}:{row['id']}"
        if key in seen:
            return
        seen.add(key)
        items.append(row)

    if app_user_id:
        try:
            app_leads = _fetchall_dict(
                """
                SELECT id, name, phone, email, city, state, address, stage, status,
                       property_type, roof_type, electricity_bill, next_followup, created_at,
                       estimated_value, user_app_id
                FROM leads_lead
                WHERE user_app_id = %s
                ORDER BY created_at DESC NULLS LAST
                LIMIT 500
                """,
                [app_user_id],
            )
            for r in app_leads:
                stage = map_crm_stage_to_pipeline(r.get("stage") or r.get("status"))
                push(
                    {
                        "id": str(r["id"]),
                        "source": "app_lead",
                        "name": r.get("name"),
                        "customer": r.get("name"),
                        "phone": r.get("phone"),
                        "email": r.get("email"),
                        "city": r.get("city"),
                        "location": ", ".join(
                            [x for x in (r.get("city"), r.get("state")) if x]
                        )
                        or r.get("address")
                        or "",
                        "capacity": None,
                        "capacityKwp": 0,
                        "stage": stage,
                        "status": r.get("status") or r.get("stage"),
                        "progress": progress_for_stage(stage),
                        "nextAction": "Follow up" if r.get("next_followup") else "Qualify lead",
                        "followUp": r.get("next_followup"),
                        "createdAt": r.get("created_at"),
                        "estimatedValue": float(r.get("estimated_value") or 0),
                        "propertyType": r.get("property_type"),
                        "roof": r.get("roof_type"),
                        "bill": r.get("electricity_bill"),
                    }
                )
        except Exception:
            pass

    if auth_user_ids:
        try:
            crm = _fetchall_dict(
                """
                SELECT id, name, phone, email, city, state, address, stage, assigned_to_id,
                       estimated_value, next_followup, created, property_type, roof_type,
                       electricity_bill
                FROM crm_leads_lead
                WHERE assigned_to_id = ANY(%s)
                ORDER BY created DESC NULLS LAST
                LIMIT 500
                """,
                [auth_user_ids],
            )
            for r in crm:
                stage = map_crm_stage_to_pipeline(r.get("stage"))
                push(
                    {
                        "id": str(r["id"]),
                        "source": "crm_lead",
                        "name": r.get("name"),
                        "customer": r.get("name"),
                        "phone": r.get("phone"),
                        "email": r.get("email"),
                        "city": r.get("city"),
                        "location": ", ".join(
                            [x for x in (r.get("city"), r.get("state")) if x]
                        )
                        or r.get("address")
                        or "",
                        "capacity": None,
                        "capacityKwp": 0,
                        "stage": stage,
                        "status": r.get("stage"),
                        "progress": progress_for_stage(stage),
                        "nextAction": "Follow up"
                        if r.get("next_followup")
                        else "Continue pipeline",
                        "followUp": r.get("next_followup"),
                        "createdAt": r.get("created"),
                        "estimatedValue": float(r.get("estimated_value") or 0),
                        "propertyType": r.get("property_type"),
                        "roof": r.get("roof_type"),
                        "bill": r.get("electricity_bill"),
                    }
                )
        except Exception:
            pass

        try:
            display = str(ctx.get("displayName") or "").lower()
            quotes = _fetchall_dict(
                """
                SELECT id, consumer_name, consumer_mobile, consumer_address1, status,
                       dc_capacity, final_amount, created_at, date,
                       assigned_associate_id, created_by_id, employee_name, lead_id
                FROM quotation_quotation
                WHERE created_by_id = ANY(%s)
                   OR assigned_associate_id = ANY(%s)
                   OR LOWER(COALESCE(employee_name,'')) LIKE '%%' || %s || '%%'
                ORDER BY COALESCE(created_at, date) DESC NULLS LAST
                LIMIT 300
                """,
                [auth_user_ids, auth_user_ids, display],
            )
            for r in quotes:
                stage = map_quote_status_to_pipeline(r.get("status"))
                kw = float(r.get("dc_capacity") or 0)
                push(
                    {
                        "id": f"q-{r['id']}",
                        "source": "quotation",
                        "name": r.get("consumer_name"),
                        "customer": r.get("consumer_name"),
                        "phone": r.get("consumer_mobile"),
                        "location": r.get("consumer_address1") or "",
                        "city": None,
                        "capacity": f"{kw:.2f} kWp" if kw > 0 else None,
                        "capacityKwp": kw,
                        "stage": stage,
                        "status": r.get("status"),
                        "progress": progress_for_stage(stage),
                        "nextAction": "Follow quote"
                        if stage == "Quotation"
                        else "Continue",
                        "createdAt": r.get("created_at") or r.get("date"),
                        "estimatedValue": float(r.get("final_amount") or 0),
                        "quotedAmount": float(r.get("final_amount") or 0),
                    }
                )
        except Exception:
            pass

        try:
            surveys = _fetchall_dict(
                """
                SELECT s.id, s.status, s.scheduled_date, s.completed_date, s.recommended_size,
                       s.created_by_id, s.engineer_id, s.lead_id,
                       l.name AS lead_name, l.phone AS lead_phone, l.city AS lead_city
                FROM surveys_survey s
                LEFT JOIN crm_leads_lead l ON l.id = s.lead_id
                WHERE s.created_by_id = ANY(%s)
                   OR s.engineer_id = ANY(%s)
                   OR l.assigned_to_id = ANY(%s)
                ORDER BY COALESCE(s.scheduled_date, s.created) DESC NULLS LAST
                LIMIT 200
                """,
                [auth_user_ids, auth_user_ids, auth_user_ids],
            )
            for r in surveys:
                stage = "Site Survey"
                kw = float(r.get("recommended_size") or 0)
                push(
                    {
                        "id": f"s-{r['id']}",
                        "source": "survey",
                        "name": r.get("lead_name") or f"Survey #{r['id']}",
                        "customer": r.get("lead_name") or f"Survey #{r['id']}",
                        "phone": r.get("lead_phone"),
                        "location": r.get("lead_city") or "",
                        "city": r.get("lead_city"),
                        "capacity": f"{kw:.2f} kWp" if kw > 0 else None,
                        "capacityKwp": kw,
                        "stage": stage,
                        "status": r.get("status"),
                        "progress": progress_for_stage(stage),
                        "nextAction": "Prepare quotation"
                        if str(r.get("status") or "").lower() == "completed"
                        else "Complete survey",
                        "followUp": r.get("scheduled_date"),
                        "createdAt": r.get("scheduled_date") or r.get("completed_date"),
                        "surveyDate": r.get("scheduled_date"),
                    }
                )
        except Exception:
            pass

        try:
            customers = _fetchall_dict(
                """
                SELECT cust_id, consumer, first_name, last_name, middle_name, comp_name,
                       city, state, address, plant_capacity, phone, email, cust_type,
                       project_type, emp_id_id
                FROM customer
                WHERE emp_id_id = ANY(%s)
                ORDER BY cust_id DESC
                LIMIT 500
                """,
                [auth_user_ids],
            )
            for c in customers:
                result = fetch_customer_result(c)
                result_status = compute_project_status(result)
                stage = "Deployed" if result_status == "Completed" else "Installation"
                name = (
                    c.get("comp_name")
                    or f"{c.get('first_name') or ''} {c.get('middle_name') or ''} {c.get('last_name') or ''}".strip()
                    or f"AF#{c.get('consumer') or c.get('cust_id')}"
                )
                kw = float(c.get("plant_capacity") or 0)
                push(
                    {
                        "id": str(c["cust_id"]),
                        "source": "project",
                        "name": name,
                        "customer": name,
                        "phone": str(c["phone"]) if c.get("phone") is not None else None,
                        "email": c.get("email"),
                        "location": ", ".join(
                            [x for x in (c.get("city"), c.get("state")) if x]
                        )
                        or c.get("address")
                        or "",
                        "city": c.get("city"),
                        "capacity": f"{kw:.2f} kWp" if kw > 0 else None,
                        "capacityKwp": kw,
                        "stage": stage,
                        "status": result_status,
                        "progress": progress_for_stage(stage),
                        "nextAction": "Monitor"
                        if stage == "Deployed"
                        else "Update installation",
                        "type": c.get("cust_type") or c.get("project_type"),
                        "createdAt": None,
                    }
                )
        except Exception:
            pass

    return items


def _json_safe(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def build_pipeline(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pipeline = []
    for meta in STAGE_META:
        stage_items = [i for i in items if i.get("stage") == meta["stage"]]
        value = sum(float(i.get("estimatedValue") or 0) for i in stage_items)
        insight = f"{len(stage_items)} projects"
        if meta["stage"] == "Quotation" and value > 0:
            insight = f"₹{(value / 100000):.1f}L quoted"
        elif meta["stage"] == "Lead":
            insight = f"{len(stage_items)} open"
        elif meta["stage"] == "Site Survey":
            insight = f"{sum(1 for i in stage_items if i.get('source') == 'survey')} surveys"
        pipeline.append(
            {
                "stage": meta["stage"],
                "count": len(stage_items),
                "insight": insight,
                "color": meta["color"],
                "icon": meta["icon"],
            }
        )
    return pipeline


def build_overview(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(items)
    completed = sum(1 for i in items if i.get("stage") == "Deployed")
    in_progress = sum(
        1
        for i in items
        if i.get("stage") in ("Site Survey", "Quotation", "Approval", "Installation")
    )
    pending = sum(1 for i in items if i.get("stage") in ("Lead", "Approval"))
    capacity = sum(float(i.get("capacityKwp") or 0) for i in items)
    return {
        "totalProjects": total,
        "inProgress": in_progress,
        "pendingAction": pending,
        "completed": completed,
        "deployed": completed,
        "awaitingAction": pending,
        "totalCapacityKwp": round(capacity * 100) / 100,
    }


def build_tasks(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tasks = []
    for i in items:
        follow = i.get("followUp")
        if follow:
            d = follow if isinstance(follow, datetime) else datetime.fromisoformat(str(follow).replace("Z", "+00:00").split("+")[0])
            d_day = d.replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
            due_label = (
                "Today"
                if d_day.date() == today.date()
                else d.strftime("%d %b %Y")
            )
            tasks.append(
                {
                    "title": "Site Survey Visit"
                    if i.get("stage") == "Site Survey"
                    else "Follow up with Customer",
                    "project": i.get("name"),
                    "due": due_label,
                    "urgent": due_label == "Today" or d_day < today,
                    "stage": i.get("stage"),
                    "projectId": i.get("id"),
                }
            )
        elif i.get("stage") == "Quotation":
            tasks.append(
                {
                    "title": "Submit Quotation",
                    "project": i.get("name"),
                    "due": "Upcoming",
                    "urgent": False,
                    "stage": i.get("stage"),
                    "projectId": i.get("id"),
                }
            )
    return tasks[:20]


def build_activities(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    activities = []
    for i in items:
        raw = i.get("followUp") or i.get("surveyDate")
        if not raw:
            continue
        d = raw if isinstance(raw, datetime) else datetime.fromisoformat(str(raw).replace("Z", "+00:00").split("+")[0])
        activities.append(
            {
                "time": d.strftime("%I:%M %p"),
                "title": "Site Survey"
                if i.get("stage") == "Site Survey"
                else "Follow up Call",
                "subtitle": i.get("name"),
                "date": d.isoformat(),
            }
        )
    return activities[:8]


def build_dashboard_payload(ctx: Dict[str, Any], items: List[Dict[str, Any]]) -> Dict[str, Any]:
    overview = build_overview(items)
    pipeline = build_pipeline(items)
    tasks = build_tasks(items)
    activities = build_activities(items)[:5]
    recent = [
        {
            "name": i.get("name"),
            "customer": i.get("customer"),
            "capacity": i.get("capacity") or "—",
            "location": i.get("location") or i.get("city") or "—",
            "type": i.get("type") or "",
            "stage": i.get("stage"),
            "progress": i.get("progress"),
            "id": i.get("id"),
            "source": i.get("source"),
        }
        for i in items
        if i.get("source") in ("project", "quotation") or i.get("stage") != "Lead"
    ][:8]
    if not recent:
        recent = [
            {
                "name": i.get("name"),
                "customer": i.get("customer"),
                "capacity": i.get("capacity") or "—",
                "location": i.get("location") or "—",
                "type": i.get("type") or "",
                "stage": i.get("stage"),
                "progress": i.get("progress"),
                "id": i.get("id"),
                "source": i.get("source"),
            }
            for i in items[:5]
        ]

    today = datetime.now()
    site_visits_today = 0
    for i in items:
        raw = i.get("surveyDate") or i.get("followUp")
        if not raw or i.get("stage") != "Site Survey":
            continue
        d = raw if isinstance(raw, datetime) else datetime.fromisoformat(str(raw).replace("Z", "+00:00").split("+")[0])
        if d.date() == today.date():
            site_visits_today += 1

    tasks_due_today = sum(1 for t in tasks if t.get("due") == "Today")
    est_gen = round(overview["totalCapacityKwp"] * 4 * 10) / 10
    survey_count = next((p["count"] for p in pipeline if p["stage"] == "Site Survey"), 0)

    return _json_safe(
        {
            "success": True,
            "associate": {
                "id": ctx.get("appUserId"),
                "name": ctx.get("displayName"),
                "fullName": ctx.get("name"),
                "email": ctx.get("email"),
                "linkedAuthUserIds": ctx.get("authUserIds") or [],
            },
            "overview": overview,
            "pipeline": pipeline,
            "tasks": tasks[:10],
            "activities": activities,
            "recentProjects": recent,
            "snapshot": {
                "capacityPlannedKwp": overview["totalCapacityKwp"],
                "estGenerationKwh": est_gen,
                "siteVisits": site_visits_today,
                "tasksDueToday": tasks_due_today,
            },
            "insights": {
                "pipelineValueLakh": round(
                    (sum(float(i.get("estimatedValue") or 0) for i in items) / 100000)
                    * 100
                )
                / 100,
                "surveysDue": survey_count,
                "followUps": tasks_due_today,
                "estGenKwh": est_gen,
            },
        }
    )


def build_projects_payload(
    ctx: Dict[str, Any], items: List[Dict[str, Any]], stage: str, q: str
) -> Dict[str, Any]:
    filtered = list(items)
    stage = (stage or "All").strip()
    q = (q or "").strip().lower()
    if stage and stage.lower() != "all":
        needle = "site survey" if stage.lower() == "survey" else stage.lower()
        filtered = [i for i in filtered if needle in str(i.get("stage") or "").lower()]
    if q:
        filtered = [
            i
            for i in filtered
            if q
            in f"{i.get('name')}{i.get('customer')}{i.get('location')}{i.get('phone')}{i.get('city')}".lower()
        ]
    return _json_safe(
        {
            "success": True,
            "count": len(filtered),
            "projects": filtered,
            "associate": {
                "id": ctx.get("appUserId"),
                "name": ctx.get("displayName"),
                "linkedAuthUserIds": ctx.get("authUserIds") or [],
            },
        }
    )


def build_tasks_payload(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    tasks = build_tasks(items)
    today = [t for t in tasks if t.get("due") == "Today"]
    overdue = [t for t in tasks if t.get("urgent") and t.get("due") != "Today"]
    upcoming = [t for t in tasks if not t.get("urgent") and t.get("due") != "Today"]
    return _json_safe(
        {
            "success": True,
            "today": today,
            "upcoming": upcoming,
            "overdue": overdue,
            "completed": [],
            "all": tasks,
        }
    )
