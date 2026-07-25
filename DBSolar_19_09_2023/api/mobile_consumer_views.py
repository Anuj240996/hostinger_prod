"""Option A consumer APIs — login, projects, complaints, services (phone JSON contracts)."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .associate_services import (
    _bit_true,
    _fetchall_dict,
    _fetchone_dict,
    _json_safe,
    compute_project_status,
    fetch_customer_result,
)


def _internal_key_ok(request) -> bool:
    expected = (os.environ.get("DJANGO_INTERNAL_API_KEY") or "").strip()
    if not expected:
        return True
    return (request.headers.get("X-Internal-Key") or "").strip() == expected


def _parse_body(request) -> Dict[str, Any]:
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def _check_user_app_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    # bcrypt from phone signup
    if hashed.startswith("$2a$") or hashed.startswith("$2b$") or hashed.startswith("$2y$"):
        try:
            import bcrypt

            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    # Django-style hash accidentally stored
    try:
        return check_password(plain, hashed)
    except Exception:
        return False


def _hash_user_app_password(plain: str) -> str:
    import bcrypt

    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def resolve_session_context(request) -> Optional[Dict[str, Any]]:
    """Build access context from phone BFF headers after JWT verify."""
    source = (request.headers.get("X-Auth-Source") or "").strip().lower()
    raw_id = request.headers.get("X-Auth-User-Id") or request.headers.get("X-App-User-Id")
    try:
        user_id = int(raw_id)
    except (TypeError, ValueError):
        return None

    app_user_id = None
    auth_user_id = None
    if source == "user_app":
        app_user_id = user_id
    elif source == "auth_user":
        auth_user_id = user_id
    else:
        # Try both
        app_user_id = user_id

    linked: List[int] = []
    if app_user_id is not None:
        try:
            rows = _fetchall_dict(
                "SELECT auth_user_id FROM app_auth_links WHERE app_user_id = %s",
                [app_user_id],
            )
            linked = [int(r["auth_user_id"]) for r in rows if r.get("auth_user_id") is not None]
        except Exception:
            linked = []
        if auth_user_id is None and linked:
            auth_user_id = linked[0]

    if auth_user_id is not None and auth_user_id not in linked:
        linked = list(dict.fromkeys([auth_user_id, *linked]))

    if app_user_id is None and auth_user_id is not None:
        try:
            row = _fetchone_dict(
                "SELECT app_user_id FROM app_auth_links WHERE auth_user_id = %s "
                "ORDER BY id DESC LIMIT 1",
                [auth_user_id],
            )
            if row and row.get("app_user_id") is not None:
                app_user_id = int(row["app_user_id"])
        except Exception:
            pass

    app_owner_id = app_user_id if app_user_id is not None else auth_user_id
    if app_owner_id is None:
        return None
    return {
        "source": source or ("user_app" if app_user_id else "auth_user"),
        "appUserId": app_user_id,
        "authUserId": auth_user_id,
        "appOwnerId": app_owner_id,
        "linkedAuthIds": linked,
        "accountIds": list(
            dict.fromkeys(
                [x for x in [app_owner_id, auth_user_id, *linked] if x is not None]
            )
        ),
    }


def _media_base() -> str:
    return (os.environ.get("MEDIA_BASE_URL") or os.environ.get("PUBLIC_BASE_URL") or "").rstrip(
        "/"
    )


def _project_type_key(customer: Dict[str, Any]) -> Optional[str]:
    tokens = [
        str(customer.get("cust_type") or "").lower(),
        str(customer.get("project_type") or "").lower(),
    ]
    for value in tokens:
        if not value or value in ("null", "n/a", "na"):
            continue
        if "industr" in value:
            return "industrial"
        if "commer" in value or "commers" in value:
            return "commercial"
        if "resid" in value or "rooftop" in value:
            return "residential"
        if "govern" in value or "goverment" in value:
            return "government"
        if any(x in value for x in ("water", "pump", "agricultur", "agri", "farm")):
            return "water_pump"
    solar_pump = customer.get("solar_pump")
    if solar_pump not in (None, "", 0, "0", "false", "null", "n"):
        return "water_pump"
    return None


def map_customer_to_project(customer: Dict[str, Any], status: str) -> Dict[str, Any]:
    name = (
        customer.get("comp_name")
        or f"{customer.get('first_name') or ''} {customer.get('middle_name') or ''} {customer.get('last_name') or ''}".strip()
        or f"AF#{customer.get('consumer') or customer.get('cust_id')}"
    )
    key = _project_type_key(customer)
    base = _media_base()
    image = None
    if key:
        rel = f"/media/project_types/{key}.jpg"
        image = f"{base}{rel}" if base else rel
    capacity = customer.get("plant_capacity")
    return {
        "id": customer.get("cust_id"),
        "projectId": customer.get("cust_id"),
        "projectName": name,
        "consumer": customer.get("consumer"),
        "city": customer.get("city"),
        "state": customer.get("state"),
        "location": (
            f"{customer.get('city') or ''}, {customer.get('state') or ''}".strip(", ")
            or customer.get("address")
            or "N/A"
        ),
        "plant_capacity": capacity,
        "plantCapacity": str(capacity) if capacity not in (None, "") and float(capacity or 0) > 0 else "0",
        "qunt_solar": customer.get("qunt_solar"),
        "quntSolar": customer.get("qunt_solar"),
        "cust_type": customer.get("cust_type"),
        "custType": customer.get("cust_type"),
        "project_type": customer.get("project_type"),
        "projectType": customer.get("project_type"),
        "solar_pump": customer.get("solar_pump"),
        "po_date": customer.get("po_date"),
        "poDate": customer.get("po_date"),
        "customerId": customer.get("cust_id"),
        "totalGeneration": None,
        "todayGeneration": None,
        "projectImage": image,
        "status": status,
    }


CUSTOMER_SELECT = """
cust_id, consumer, first_name, last_name, middle_name,
email, phone, address, city, state, comp_name, new_customer_id, plant_capacity, qunt_solar,
cust_type, project_type, po_date, solar_pump
"""


def load_projects_for_context(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    app_user_id = ctx.get("appUserId")
    if app_user_id is not None:
        try:
            rows = _fetchall_dict(
                f"""
                SELECT {CUSTOMER_SELECT}
                FROM customer
                WHERE new_customer_id::bigint IN (
                  SELECT auth_user_id FROM app_auth_links WHERE app_user_id = %s
                )
                ORDER BY cust_id DESC
                """,
                [app_user_id],
            )
        except Exception:
            rows = []

    if not rows:
        owner_ids = list(ctx.get("linkedAuthIds") or [])
        if ctx.get("authUserId") is not None:
            owner_ids = list(dict.fromkeys([ctx["authUserId"], *owner_ids]))
        if owner_ids:
            try:
                rows = _fetchall_dict(
                    f"""
                    SELECT {CUSTOMER_SELECT}
                    FROM customer
                    WHERE new_customer_id::bigint = ANY(%s)
                    ORDER BY cust_id DESC
                    """,
                    [owner_ids],
                )
            except Exception:
                rows = []

    projects = []
    for c in rows:
        result = fetch_customer_result(c)
        status = compute_project_status(result)
        projects.append(map_customer_to_project(c, status))
    return projects


def _parse_legacy_complaint_message(message: str) -> Tuple[str, str, str]:
    import re

    m = re.search(
        r"\[Category:\s*([^\]]+)\]\s*\[Title:\s*([^\]]+)\]\s*(?:\n\n|\s+)?(.*)",
        message or "",
        re.S,
    )
    if not m:
        return "", "", message or ""
    return m.group(1).strip(), m.group(2).strip(), (m.group(3) or "").strip()


def list_complaints(ctx: Dict[str, Any], cust_id: Optional[int] = None) -> List[Dict[str, Any]]:
    account_ids = ctx.get("accountIds") or [ctx["appOwnerId"]]
    app_user_id = ctx.get("appUserId")
    params: List[Any] = [app_user_id, account_ids]
    filter_sql = ""
    if cust_id:
        owner = _fetchone_dict(
            "SELECT new_customer_id FROM customer WHERE cust_id = %s LIMIT 1", [cust_id]
        )
        if owner and owner.get("new_customer_id") is not None:
            filter_sql = " AND (f.account_id = %s OR f.app_user_id = %s)"
            params.extend([int(owner["new_customer_id"]), app_user_id])

    rows = _fetchall_dict(
        f"""
        SELECT f.id, f.fullname, f.mobilenumber, f."Location" AS location, f.message,
               f.status, f.postingdate, f.account_id, f.assignto_id, f.assignedtime,
               f.updationdate, f.category, f.title, f.warranty_type, f.app_user_id,
               u.first_name, u.last_name, u.email AS engineer_email,
               up.phone AS engineer_phone, up.image AS engineer_image
        FROM firereport_firereport f
        LEFT JOIN auth_user u ON u.id = f.assignto_id
        LEFT JOIN user_profile up ON up.customer_id = u.id
        WHERE (
            (f.app_user_id IS NOT NULL AND f.app_user_id = %s)
            OR (f.account_id = ANY(%s))
        )
        {filter_sql}
        ORDER BY f.postingdate DESC NULLS LAST, f.id DESC
        LIMIT 500
        """,
        params,
    )
    out = []
    for r in rows:
        cat = r.get("category") or ""
        title = r.get("title") or ""
        desc = r.get("message") or ""
        if not cat and not title:
            cat, title, desc = _parse_legacy_complaint_message(r.get("message") or "")
        eng = None
        if r.get("assignto_id"):
            eng_name = f"{r.get('first_name') or ''} {r.get('last_name') or ''}".strip()
            eng = {
                "id": r.get("assignto_id"),
                "name": eng_name or None,
                "email": r.get("engineer_email"),
                "phone": r.get("engineer_phone"),
                "photo": r.get("engineer_image"),
            }
        out.append(
            {
                "id": r.get("id"),
                "userId": r.get("account_id"),
                "appUserId": r.get("app_user_id"),
                "category": cat,
                "warrantyType": r.get("warranty_type"),
                "title": title,
                "description": desc,
                "message": r.get("message"),
                "status": (r.get("status") or "pending").lower()
                if r.get("status")
                else "pending",
                "createdAt": r.get("postingdate"),
                "postingdate": r.get("postingdate"),
                "updatedAt": r.get("updationdate"),
                "fullName": r.get("fullname"),
                "mobileNumber": r.get("mobilenumber"),
                "location": r.get("location"),
                "assignToId": r.get("assignto_id"),
                "assignedTime": r.get("assignedtime"),
                "engineer": eng,
            }
        )
    return out


def create_complaint(ctx: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
    category = str(body.get("category") or "").strip()
    title = str(body.get("title") or "").strip()
    description = str(body.get("description") or body.get("message") or "").strip()
    warranty = str(body.get("warrantyType") or body.get("warranty_type") or "").strip() or None
    message = f"[Category: {category}] [Title: {title}]\n\n{description}".strip()
    account_id = ctx.get("authUserId") or ctx.get("appOwnerId")
    full_name = str(body.get("fullName") or body.get("name") or "NA")
    mobile = str(body.get("mobileNumber") or body.get("phone") or "0")
    location = str(body.get("location") or "")

    cust_id = body.get("cust_id")
    if cust_id:
        try:
            cust = _fetchone_dict(
                "SELECT first_name, last_name, phone, address, city, new_customer_id "
                "FROM customer WHERE cust_id = %s LIMIT 1",
                [int(cust_id)],
            )
            if cust:
                full_name = (
                    f"{cust.get('first_name') or ''} {cust.get('last_name') or ''}".strip()
                    or full_name
                )
                mobile = str(cust.get("phone") or mobile)
                location = cust.get("city") or cust.get("address") or location
                if cust.get("new_customer_id") is not None:
                    account_id = int(cust["new_customer_id"])
        except Exception:
            pass

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO firereport_firereport
              (fullname, mobilenumber, "Location", message, status, postingdate,
               account_id, assignby, category, title, warranty_type, app_user_id)
            VALUES (%s,%s,%s,%s,%s,NOW(),%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            [
                full_name,
                mobile,
                location,
                message,
                "Pending",
                account_id,
                account_id,
                category or None,
                title or None,
                warranty,
                ctx.get("appUserId"),
            ],
        )
        new_id = cursor.fetchone()[0]

    items = list_complaints(ctx)
    for item in items:
        if item.get("id") == new_id:
            return item
    return {"id": new_id, "status": "pending", "category": category, "title": title}


def list_services(ctx: Dict[str, Any], cust_id: Optional[int] = None) -> List[Dict[str, Any]]:
    account_ids = ctx.get("accountIds") or [ctx["appOwnerId"]]
    app_user_id = ctx.get("appUserId")
    filter_auth = None
    if cust_id:
        owner = _fetchone_dict(
            "SELECT new_customer_id FROM customer WHERE cust_id = %s LIMIT 1", [cust_id]
        )
        if owner and owner.get("new_customer_id") is not None:
            filter_auth = int(owner["new_customer_id"])

    rows = _fetchall_dict(
        """
        SELECT sr.id, sr.fullname, sr.mobilenumber, sr."Location" AS location, sr.message,
               sr.status, sr.postingdate, sr.account_id, sr.assignto_id, sr.assignedtime,
               sr.service_type, sr.additional_notes, sr.warranty_type, sr.app_user_id,
               u.first_name, u.last_name, u.email AS engineer_email,
               up.phone AS engineer_phone, up.image AS engineer_image
        FROM firereport_servicerequest sr
        LEFT JOIN auth_user u ON u.id = sr.assignto_id
        LEFT JOIN user_profile up ON up.customer_id = u.id
        WHERE (
            (sr.app_user_id IS NOT NULL AND sr.app_user_id = %s)
            OR (sr.account_id = ANY(%s))
            OR (%s IS NOT NULL AND sr.account_id = %s)
        )
        ORDER BY sr.postingdate DESC NULLS LAST, sr.id DESC
        LIMIT 500
        """,
        [app_user_id, account_ids, filter_auth, filter_auth],
    )
    out = []
    for r in rows:
        eng = None
        if r.get("assignto_id"):
            eng = {
                "id": r.get("assignto_id"),
                "name": f"{r.get('first_name') or ''} {r.get('last_name') or ''}".strip()
                or None,
                "email": r.get("engineer_email"),
                "phone": r.get("engineer_phone"),
                "photo": r.get("engineer_image"),
            }
        out.append(
            {
                "id": r.get("id"),
                "fullName": r.get("fullname"),
                "mobileNumber": r.get("mobilenumber"),
                "location": r.get("location"),
                "message": r.get("message"),
                "serviceType": r.get("service_type"),
                "additionalNotes": r.get("additional_notes"),
                "warrantyType": r.get("warranty_type"),
                "status": r.get("status") or "Pending",
                "createdAt": r.get("postingdate"),
                "postingdate": r.get("postingdate"),
                "accountId": r.get("account_id"),
                "appUserId": r.get("app_user_id"),
                "assignToId": r.get("assignto_id"),
                "assignedTime": r.get("assignedtime"),
                "engineer": eng,
            }
        )
    return out


def create_service(ctx: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
    service_type = str(body.get("serviceType") or body.get("service_type") or "Other").strip()
    notes = str(body.get("additionalNotes") or body.get("additional_notes") or "").strip() or None
    warranty = str(body.get("warrantyType") or body.get("warranty_type") or "").strip() or None
    message = str(body.get("message") or service_type)
    account_id = ctx.get("authUserId") or ctx.get("appOwnerId")
    full_name = str(body.get("fullName") or "NA")
    mobile = str(body.get("mobileNumber") or body.get("phone") or "0")
    location = str(body.get("location") or "")

    cust_id = body.get("cust_id")
    if cust_id:
        try:
            cust = _fetchone_dict(
                "SELECT first_name, last_name, phone, address, city, new_customer_id "
                "FROM customer WHERE cust_id = %s LIMIT 1",
                [int(cust_id)],
            )
            if cust:
                full_name = (
                    f"{cust.get('first_name') or ''} {cust.get('last_name') or ''}".strip()
                    or full_name
                )
                mobile = str(cust.get("phone") or mobile)
                location = cust.get("city") or cust.get("address") or location
                if cust.get("new_customer_id") is not None:
                    account_id = int(cust["new_customer_id"])
        except Exception:
            pass

    parts = []
    if warranty:
        parts.append(f"[Warranty: {warranty}]")
    if service_type:
        parts.append(f"[Type: {service_type}]")
    if message:
        parts.append(message)
    if notes:
        parts.append(notes)
    legacy_message = " ".join(parts).strip() or service_type

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO firereport_servicerequest
              (fullname, mobilenumber, "Location", message, status, postingdate,
               account_id, assignby, service_type, additional_notes, warranty_type, app_user_id)
            VALUES (%s,%s,%s,%s,%s,NOW(),%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            [
                full_name,
                mobile,
                location,
                legacy_message,
                "Pending",
                account_id,
                account_id,
                service_type,
                notes,
                warranty,
                ctx.get("appUserId"),
            ],
        )
        new_id = cursor.fetchone()[0]

    for item in list_services(ctx):
        if item.get("id") == new_id:
            return item
    return {"id": new_id, "status": "Pending", "serviceType": service_type}


# ---- Views ----


@csrf_exempt
@require_http_methods(["POST"])
def consumer_login(request):
    body = _parse_body(request)
    username = str(body.get("username") or "").strip()
    password = body.get("password") or ""
    if not username or not password:
        return JsonResponse(
            {"success": False, "message": "Validation failed"}, status=400
        )

    # 1) user_app
    try:
        ua = _fetchone_dict(
            """
            SELECT id, name, email, phone, password_hash, role, address, created_at
            FROM user_app
            WHERE LOWER(TRIM(email)) = LOWER(TRIM(%s))
            LIMIT 1
            """,
            [username],
        )
    except Exception:
        ua = None

    if ua and _check_user_app_password(password, ua.get("password_hash") or ""):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_app SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                    [ua["id"]],
                )
        except Exception:
            pass
        role = ua.get("role") or "customer"
        name_l = str(ua.get("name") or "").lower()
        email_l = str(ua.get("email") or "").lower()
        if role == "associate" or name_l.startswith("aso_") or email_l.startswith("aso_"):
            role = "associate"
        return JsonResponse(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "token": None,
                    "user": {
                        "id": ua["id"],
                        "name": ua.get("name"),
                        "email": ua.get("email"),
                        "phone": ua.get("phone"),
                        "role": role,
                        "address": ua.get("address"),
                        "createdAt": ua.get("created_at"),
                        "source": "user_app",
                    },
                },
            }
        )

    # 2) auth_user
    user = User.objects.filter(username__iexact=username).first() or User.objects.filter(
        email__iexact=username
    ).first()
    if not user:
        return JsonResponse({"success": False, "message": "Invalid credentials"}, status=401)
    auth_user = authenticate(username=user.username, password=password)
    if not auth_user:
        return JsonResponse({"success": False, "message": "Invalid credentials"}, status=401)

    display = (
        f"{auth_user.first_name or ''} {auth_user.last_name or ''}".strip()
        or auth_user.username
        or auth_user.email
        or username
    )
    login_l = username.lower()
    username_l = (auth_user.username or "").lower()
    role = "associate" if login_l.startswith("aso_") or username_l.startswith("aso_") else "customer"
    return JsonResponse(
        {
            "success": True,
            "message": "Login successful",
            "data": {
                "token": None,
                "user": {
                    "id": auth_user.id,
                    "name": display,
                    "email": auth_user.email or username,
                    "phone": "",
                    "role": role,
                    "address": "",
                    "source": "auth_user",
                },
            },
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def consumer_signup(request):
    body = _parse_body(request)
    name = str(body.get("name") or "").strip()
    email = str(body.get("email") or "").strip()
    phone = str(body.get("phone") or "").strip()
    password = body.get("password") or ""
    address = str(body.get("address") or "").strip() or None
    role = str(body.get("role") or "customer").strip() or "customer"
    if not name or not email or not password:
        return JsonResponse({"success": False, "message": "Validation failed"}, status=400)

    existing = _fetchone_dict(
        "SELECT id FROM user_app WHERE LOWER(TRIM(email)) = LOWER(TRIM(%s)) LIMIT 1",
        [email],
    )
    if existing:
        return JsonResponse(
            {"success": False, "message": "Email already registered"}, status=400
        )

    pw_hash = _hash_user_app_password(password)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_app (name, email, phone, password_hash, role, address, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,NOW())
            RETURNING id, name, email, phone, role, address, created_at
            """,
            [name, email, phone, pw_hash, role, address],
        )
        row = cursor.fetchone()
    return JsonResponse(
        {
            "success": True,
            "message": "Signup successful",
            "data": {
                "token": None,
                "user": {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "role": row[4],
                    "address": row[5],
                    "createdAt": row[6],
                    "source": "user_app",
                },
            },
        }
    )


def _require_ctx(request):
    if not _internal_key_ok(request):
        return None, JsonResponse({"message": "Unauthorized"}, status=401)
    ctx = resolve_session_context(request)
    if not ctx:
        return None, JsonResponse({"message": "Could not identify user"}, status=401)
    return ctx, None


@require_GET
def projects_list(request):
    ctx, err = _require_ctx(request)
    if err:
        return err
    projects = load_projects_for_context(ctx)
    if not projects:
        return JsonResponse(
            {"projects": [], "message": "No projects found for this user"}
        )
    return JsonResponse(_json_safe({"projects": projects}))


@require_GET
def complaints_list(request):
    ctx, err = _require_ctx(request)
    if err:
        return err
    cust_id = request.GET.get("cust_id")
    try:
        cust_id_i = int(cust_id) if cust_id else None
    except ValueError:
        cust_id_i = None
    try:
        return JsonResponse(
            _json_safe({"complaints": list_complaints(ctx, cust_id_i)})
        )
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def complaints_create(request):
    ctx, err = _require_ctx(request)
    if err:
        return err
    try:
        item = create_complaint(ctx, _parse_body(request))
        return JsonResponse(_json_safe(item), status=201)
    except Exception as e:
        return JsonResponse({"message": str(e) or "Failed to create complaint"}, status=500)


@require_GET
def services_list(request):
    ctx, err = _require_ctx(request)
    if err:
        return err
    cust_id = request.GET.get("cust_id")
    try:
        cust_id_i = int(cust_id) if cust_id else None
    except ValueError:
        cust_id_i = None
    try:
        return JsonResponse(
            _json_safe({"serviceRequests": list_services(ctx, cust_id_i)})
        )
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def services_create(request):
    ctx, err = _require_ctx(request)
    if err:
        return err
    try:
        item = create_service(ctx, _parse_body(request))
        return JsonResponse(_json_safe(item), status=201)
    except Exception as e:
        return JsonResponse(
            {"message": str(e) or "Failed to create service request"}, status=500
        )


@require_GET
def services_remarks(request):
    if not _internal_key_ok(request):
        return JsonResponse({"message": "Unauthorized"}, status=401)
    try:
        rows = _fetchall_dict(
            "SELECT id, remark FROM firereport_serviceremarkmaster ORDER BY id"
        )
        return JsonResponse(
            {"remarks": [{"id": r["id"], "remark": r.get("remark") or ""} for r in rows]}
        )
    except Exception:
        return JsonResponse({"remarks": []})
