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
    Per-page/submodule access check.

    The four Dashboard landing URLs (staff / consumer / complaint / stock) are allowed
    only when the matching item is explicitly granted under Control Panel
    Models & Sub-models — not from Portal access alone.

    Other URLs: legacy behavior (open if no nav rows yet; else enforce nav grants).
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    if url_name in DASHBOARD_SUBMODULE_URL_NAMES:
        if not CPUserNavAccess.objects.filter(user=user).exists():
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

    if not CPUserNavAccess.objects.filter(user=user).exists():
        return True

    nav_ids = list(
        CPNavItem.objects.filter(url_name=url_name, is_active=True).values_list("id", flat=True)
    )
    if not nav_ids:
        return True

    return CPUserNavAccess.objects.filter(
        user=user,
        nav_item_id__in=nav_ids,
        granted=True,
    ).exists()

