"""
Shared permission utilities for Control Panel permissions.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    reason: str = ""


def has_cp_operation(user, module_name: str, operation: str) -> bool:
    """
    True if user has granted CP permission for given module + operation.
    Superuser bypasses.
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_superuser", False):
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


def has_portal_access(user, portal_name: str) -> bool:
    """
    Portal access is separate from module permissions.
    Superuser bypasses.
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_superuser", False):
        return True

    portal = CPPortal.objects.filter(name__iexact=portal_name, is_active=True).first()
    if not portal:
        return False

    return CPUserPortalAccess.objects.filter(user=user, portal=portal, granted=True).exists()


def has_nav_url_access(user, url_name: str) -> bool:
    """
    Per-page/submodule access check against Control Panel nav grants.

    Dashboard landing URLs always require an explicit nav grant.
    Other registered nav URLs require grant once the user has any CP nav rows.
    URLs not in CPNavItem stay open (not managed by Control Panel menus).
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    if url_name in {"user-logout", "user-login"}:
        return True

    has_any_nav = CPUserNavAccess.objects.filter(user=user).exists()

    if url_name in DASHBOARD_SUBMODULE_URL_NAMES:
        if not has_any_nav:
            return False
        nav_ids = list(
            CPNavItem.objects.filter(url_name=url_name, is_active=True).values_list("id", flat=True)
        )
        if not nav_ids:
            return False
        return CPUserNavAccess.objects.filter(
            user=user,
            nav_item_id__in=nav_ids,
            granted=True,
        ).exists()

    nav_ids = list(
        CPNavItem.objects.filter(url_name=url_name, is_active=True).values_list("id", flat=True)
    )
    # Not a Control Panel menu URL → do not block
    if not nav_ids:
        return True

    # No CP nav rows yet → legacy open access for registered URLs
    if not has_any_nav:
        return True

    return CPUserNavAccess.objects.filter(
        user=user,
        nav_item_id__in=nav_ids,
        granted=True,
    ).exists()

