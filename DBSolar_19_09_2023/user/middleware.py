from __future__ import annotations

from django.http import HttpResponseForbidden
from django.urls import resolve

from .permission_map import (
    DASHBOARD_SUBMODULE_URL_NAMES,
    PORTAL_URLS,
    PORTAL_URLS_ANY,
    required_permission,
)
from .permissions import has_cp_operation, has_portal_access, has_nav_url_access


class CPPermissionMiddleware:
    """
    Enforce Control Panel permissions at the URL layer.

    - If URL name is mapped to a portal, require portal access.
    - If URL name is mapped to a module/operation, require that operation.
    - Superusers bypass.
    - Unmapped URLs are not blocked.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce for authenticated users (login_required handles others).
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            if not getattr(user, "is_superuser", False):
                match = getattr(request, "resolver_match", None)
                if match is None:
                    try:
                        match = resolve(request.path_info)
                    except Exception:
                        match = None

                url_name = getattr(match, "url_name", None) if match else None

                # Skip admin site and control panel pages themselves
                if url_name and (
                    url_name.startswith("control_panel_")
                    or url_name in {"admin:index", "admin:login"}
                ):
                    return self.get_response(request)

                # If a page/submodule permission exists, enforce it first.
                # (This enables fine-grained "sub module" control from the control panel.)
                if url_name and not has_nav_url_access(user, url_name):
                    return HttpResponseForbidden("Access denied (submodule).")

                # Portal access checks (any-of first, then single portal).
                # Dashboard routes are already gated by has_nav_url_access (portal + submodule);
                # skipping the second portal pass avoids false "Access denied (portal)" when
                # only submodule or only portal was used to grant access.
                if url_name not in DASHBOARD_SUBMODULE_URL_NAMES:
                    portals_any = PORTAL_URLS_ANY.get(url_name or "")
                    if portals_any:
                        if not any(has_portal_access(user, p) for p in portals_any):
                            return HttpResponseForbidden("Access denied (portal).")
                    else:
                        portal = PORTAL_URLS.get(url_name or "")
                        if portal and not has_portal_access(user, portal):
                            return HttpResponseForbidden("Access denied (portal).")

                # Module/operation checks (not for the four dashboard landing URLs — access is CP portal/nav)
                perm = required_permission(url_name, request)
                if perm and url_name not in DASHBOARD_SUBMODULE_URL_NAMES:
                    module, operation = perm
                    if not has_cp_operation(user, module, operation):
                        return HttpResponseForbidden("Access denied (permission).")

        return self.get_response(request)

