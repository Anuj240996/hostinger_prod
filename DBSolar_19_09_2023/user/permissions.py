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

    Consumers (non-staff) always get Consumer Portal menu access by default.
    Control Panel nav grants apply to staff users only.

    Once a staff user has ANY Control Panel config (portal / module / nav rows),
    registered menu URLs require an explicit granted=True nav row.
    Unchecked items in Control Panel must not appear in the staff sidebar.
    """
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True

    if url_name in {"user-logout", "user-login"}:
        return True

    # Consumer / customer portal: menus are open by default (no CP grants required)
    if not getattr(user, "is_staff", False):
        return True

    has_any_nav = CPUserNavAccess.objects.filter(user=user).exists()
    has_cp_config = (
        has_any_nav
        or CPUserModulePermission.objects.filter(user=user).exists()
        or CPUserPortalAccess.objects.filter(user=user).exists()
    )

    nav_ids = list(
        CPNavItem.objects.filter(url_name=url_name, is_active=True).values_list("id", flat=True)
    )

    if url_name in DASHBOARD_SUBMODULE_URL_NAMES:
        if not nav_ids:
            return False
        return CPUserNavAccess.objects.filter(
            user=user,
            nav_item_id__in=nav_ids,
            granted=True,
        ).exists()

    # Not a Control Panel menu URL → do not block
    if not nav_ids:
        return True

    # Staff with Control Panel configuration → require explicit grant
    if has_cp_config:
        return CPUserNavAccess.objects.filter(
            user=user,
            nav_item_id__in=nav_ids,
            granted=True,
        ).exists()

    # Legacy staff with no CP rows yet
    return True

