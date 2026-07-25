"""Option A associate HTTP APIs consumed by the phone BFF."""

import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from . import associate_services as svc


def _internal_key_ok(request) -> bool:
    expected = (os.environ.get("DJANGO_INTERNAL_API_KEY") or "").strip()
    if not expected:
        # Dev fallback: allow when unset so EasyPanel can enable gradually
        return True
    provided = (request.headers.get("X-Internal-Key") or "").strip()
    return provided == expected


def _auth_user_id_from_request(request):
    raw = request.headers.get("X-Auth-User-Id") or request.GET.get("auth_user_id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _require_associate_user(request):
    if not _internal_key_ok(request):
        return None, JsonResponse({"message": "Unauthorized"}, status=401)
    auth_user_id = _auth_user_id_from_request(request)
    if not auth_user_id:
        return None, JsonResponse({"message": "Authentication required"}, status=401)
    try:
        ctx = svc.resolve_associate_context(auth_user_id)
    except ValueError as e:
        return None, JsonResponse({"message": str(e)}, status=401)
    return ctx, None


@csrf_exempt
@require_http_methods(["POST"])
def associate_login(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Invalid JSON body"}, status=400
        )

    username = str(body.get("username") or "").strip()
    password = body.get("password") or ""
    if not username or not password:
        return JsonResponse(
            {
                "success": False,
                "message": "Validation failed",
                "errors": [
                    {"msg": "Username is required", "path": "username"},
                    {"msg": "Password is required", "path": "password"},
                ],
            },
            status=400,
        )

    user = svc.authenticate_associate(username, password)
    if not user:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid associate credentials. Use your staff username from auth_user.",
            },
            status=401,
        )

    display_name = (
        f"{user.first_name or ''} {user.last_name or ''}".strip()
        or user.username
        or user.email
        or username
    )
    return JsonResponse(
        {
            "success": True,
            "message": "Login successful",
            "data": {
                # Phone BFF re-issues its own JWT; this token field is unused by mobile.
                "token": None,
                "user": {
                    "id": user.id,
                    "name": display_name,
                    "email": user.email or username,
                    "phone": "",
                    "role": "associate",
                    "address": "",
                    "username": user.username or None,
                },
            },
        }
    )


@require_GET
def associate_dashboard(request):
    ctx, err = _require_associate_user(request)
    if err:
        return err
    try:
        items = svc.load_associate_records(ctx)
        return JsonResponse(svc.build_dashboard_payload(ctx, items))
    except Exception as e:
        return JsonResponse(
            {"message": str(e) or "Failed to load associate dashboard"}, status=500
        )


@require_GET
def associate_projects(request):
    ctx, err = _require_associate_user(request)
    if err:
        return err
    try:
        items = svc.load_associate_records(ctx)
        stage = request.GET.get("stage") or "All"
        q = request.GET.get("q") or ""
        return JsonResponse(svc.build_projects_payload(ctx, items, stage, q))
    except Exception as e:
        return JsonResponse(
            {"message": str(e) or "Failed to load associate projects"}, status=500
        )


@require_GET
def associate_tasks(request):
    ctx, err = _require_associate_user(request)
    if err:
        return err
    try:
        items = svc.load_associate_records(ctx)
        return JsonResponse(svc.build_tasks_payload(items))
    except Exception as e:
        return JsonResponse(
            {"message": str(e) or "Failed to load associate tasks"}, status=500
        )
