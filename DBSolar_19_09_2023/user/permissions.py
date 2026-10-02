"""
Shared permission utilities for Control Panel permissions.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from django.contrib.auth.models import AnonymousUser

from .models import (
    CPModule,
    CPModulePermission,
    CPUserModulePermission,
    CPPortal,
    CPUserPortalAccess,
    CPNavItem,
    CPUserNavAccess,
)
from .permission_map import DASHBOARD_SUBMODULE_URL_NAMES
from .nav_registry import all_nav_specs


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    reason: str = ""


@lru_cache(maxsize=1)
def _registered_menu_url_names() -> frozenset:
    """URL names defined in Control Panel nav registry (staff menus/submenus)."""
    return frozenset(s.url_name for s in all_nav_specs() if s.url_name)


def has_portal_access(user, portal_name: str) -> bool:
    """
    Portal access is separate from module permissions.
    Superuser bypasses.
    Non-staff consumers always have access (Consumer Portal is open by default).
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_superuser", False):
        return True

    # Consumer / customer users: portal checks do not apply
    if not getattr(user, "is_staff", False):
        return True

    portal = CPPortal.objects.filter(name__iexact=portal_name, is_active=True).first()
    if not portal:
        return False

    return CPUserPortalAccess.objects.filter(user=user, portal=portal, granted=True).exists()


def has_cp_operation(user, module_name: str, operation: str) -> bool:
    """
    True if user has granted CP permission for given module + operation.
    Superuser bypasses.
    Non-staff consumers are not subject to Control Panel module grants.
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_superuser", False):
        return True

    if not getattr(user, "is_staff", False):
        return True

    module = CPModule.objects.filter(name__iexact=module_name, is_active=True).first()
    if not module:
        return False

    perm = CPModulePermission.objects.filter(
        module=module,
        operation=operation.lower(),
        is_active=True,
    ).first()
    if not perm:
        return False

    return CPUserModulePermission.objects.filter(
        user=user,
        module_permission=perm,
        granted=True,
    ).exists()


def has_cp_module_view(user, module_name: str) -> bool:
    return has_cp_operation(user, module_name, "view")


def has_nav_url_access(user, url_name: str) -> bool:
    """
    Per-page/submodule access check against Control Panel nav grants.

    Consumers (non-staff) always get Consumer Portal menu access by default.
    Control Panel nav grants apply to staff users only.

    Staff: registered menu / submenu URLs require an explicit granted=True
    Control Panel nav row. First-time staff with nothing selected in Control
    Panel must NOT see staff menus/submenus.
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    if url_name in {"user-logout", "user-login", "user:no_access", "no_access"}:
        return True

    # Consumer / customer portal: menus are open by default (no CP grants required)
    if not getattr(user, "is_staff", False):
        return True

    # Solar CRM Staff Dashboard is always available for staff (no CP checkbox required)
    if url_name == "main_project_dashboard":
        return True

    nav_ids = list(
        CPNavItem.objects.filter(url_name=url_name, is_active=True).values_list("id", flat=True)
    )

    # Dashboard landings and all other registered CP menu URLs need a grant
    if url_name in DASHBOARD_SUBMODULE_URL_NAMES or url_name in _registered_menu_url_names():
        if not nav_ids:
            # Menu exists in registry but no DB row / no grant yet → hide for staff
            return False
        return CPUserNavAccess.objects.filter(
            user=user,
            nav_item_id__in=nav_ids,
            granted=True,
        ).exists()

    # Not a Control Panel menu URL → do not block (non-menu pages)
    return True

