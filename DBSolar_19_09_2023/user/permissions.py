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

    Backward compatible behavior:
    - If the user has *no* CP nav grants configured yet, return True (do not hide menus).
    - Once any nav grants exist for the user, enforce nav-item grants for mapped url_names.
    - Unmapped url_names are allowed (so existing pages don't disappear unexpectedly).
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    # If the admin hasn't configured nav permissions at all for this user yet,
    # don't hide menus (legacy behavior).
    if not CPUserNavAccess.objects.filter(user=user).exists():
        return True

    # Multiple nav items can share the same url_name (e.g. "Search" appears under
    # different sections). Allow if user has access to ANY matching nav item.
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

