"""
Control Panel Views for Permission Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.contrib.auth import hashers
from django.utils import timezone
from django.urls import reverse
import json
import secrets
from collections import OrderedDict

from transactions.models import Vendor

from .cp_presets import OPERATIONS_ORDER, PRESETS, preset_by_key, preset_checkbox_state

# Permissions Manager v3: omitted from the "Modules & operations" table (POST must not overwrite these).
CP_PM_TABLE_HIDDEN_MODULE_NAMES = frozenset({"product"})

from .nav_registry import NAV_KEY_HIDDEN_FOR_VENDOR_PERMISSIONS, all_nav_specs
from .models import (
    CPModule,
    CPModulePermission,
    CPUserModulePermission,
    CPPortal,
    CPPortalModule,
    CPUserPortalAccess,
    CPNavItem,
    CPUserNavAccess,
    ControlPanelAccess,
    Profile,
    VendorAccount,
)


def is_admin(user):
    """Check if user is admin/superuser"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def control_panel_login(request):
    """Password-protected login page for control panel"""
    if request.method == 'POST':
        password = request.POST.get('control_panel_password', '').strip()
        
        if not password:
            messages.error(request, 'Password is required')
            return render(request, 'user/control_panel_login.html')
        
        # Get or create control panel access
        access_config, created = ControlPanelAccess.objects.get_or_create(
            id=1,
            defaults={'password_hash': hashers.make_password('admin123'), 'is_active': True}
        )
        
        # Check password
        if hashers.check_password(password, access_config.password_hash):
            # Store in session
            request.session['control_panel_authenticated'] = True
            request.session['control_panel_authenticated_at'] = timezone.now().isoformat()
            
            # Update access log
            access_config.last_accessed = timezone.now()
            access_config.last_accessed_by = request.user
            access_config.save()
            
            messages.success(request, 'Access granted to Control Panel')
            return redirect('user:control_panel_home')
        else:
            messages.error(request, 'Invalid password. Access denied.')
    
    return render(request, 'user/control_panel_login.html')


@login_required
@user_passes_test(is_admin)
def control_panel_home(request):
    """Main control panel page - shows user selection"""
    # Check if user is authenticated for control panel
    if not request.session.get('control_panel_authenticated'):
        messages.warning(request, 'Please login to Control Panel first')
        return redirect('user:control_panel_login')
    
    # Get all users (employees, customers)
    # Filter users based on their profile or groups
    users = User.objects.filter(is_active=True).select_related('profile').order_by('username')
    
    # Categorize users
    employees = []
    vendor_rows = []
    customers = []
    
    for user in users:
        # Check if user has profile with department info
        if hasattr(user, 'profile'):
            dept = user.profile.department if user.profile.department else ''
            # Associates are listed only under the Vendors tab (with vendor/associate rows), not Employees.
            if dept == "Associate":
                continue
            if (
                "Engineer" in dept
                or "Administration" in dept
                or "Finance" in dept
                or "Stockist" in dept
            ):
                employees.append(user)
            else:
                if not user.is_staff:
                    customers.append(user)
        else:
            # No profile: keep non-staff users under customer list
            if user.is_staff:
                employees.append(user)
            else:
                customers.append(user)
    
    # Load vendors from the Vendor table and show linkage to a login user
    # NOTE: Some DBs have legacy boolean columns stored as BIT/VARYING.
    # Avoid boolean filtering at SQL level here to prevent type errors.
    vendors = Vendor.objects.all().select_related("category").order_by("name")
    vendor_accounts = {}
    for va in VendorAccount.objects.select_related("vendor", "user", "user__profile").all():
        vendor_accounts[va.vendor_id] = va
    for v in vendors:
        vendor_rows.append(
            {
                "vendor": v,
                "account": vendor_accounts.get(v.id),
            }
        )

    # Associate staff: append rows into the same Vendors tab list (Control Panel).
    associate_users = list(
        User.objects.filter(is_active=True, is_staff=True, profile__department="Associate")
        .select_related("profile")
        .order_by("username")
    )
    associate_ids = [u.id for u in associate_users]
    va_by_uid = {
        va.user_id: va
        for va in VendorAccount.objects.filter(
            user_id__in=associate_ids,
            is_active=True,
        ).select_related("vendor")
    }

    vendor_tab_rows = [{"is_associate_row": False, "vendor": r["vendor"], "account": r["account"]} for r in vendor_rows]
    for u in associate_users:
        va = va_by_uid.get(u.id)
        vend_id_display = "—"
        if va is not None and getattr(va, "vendor", None) is not None:
            v = va.vendor
            vend_id_display = (v.vendor_id or str(v.pk)).strip() or "—"
        vendor_tab_rows.append(
            {
                "is_associate_row": True,
                "associate_user": u,
                "vendor_account": va,
                "vend_id_display": vend_id_display,
            }
        )

    # Check if modules exist (used by templates)
    modules = CPModule.objects.filter(is_active=True).order_by("order", "display_name")
    
    context = {
        'employees': employees,
        'vendors': vendor_rows,
        'vendor_tab_rows': vendor_tab_rows,
        'customers': customers,
        'all_users': users,
        'modules': modules,
    }
    
    return render(request, 'user/control_panel_home.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
@csrf_protect
def control_panel_create_vendor_user(request, vendor_id):
    """
    Create a login `auth.User` for a Vendor and link via VendorAccount.
    """
    if not request.session.get('control_panel_authenticated'):
        messages.warning(request, 'Please login to Control Panel first')
        return redirect('user:control_panel_login')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    if VendorAccount.objects.filter(vendor=vendor).exists():
        messages.info(request, f'Login already exists for vendor: {vendor.name}')
        return redirect('user:control_panel_home')

    # Username preference: vendor_id, else email, else vendor pk
    base_username = (vendor.vendor_id or vendor.email or f"vendor{vendor.id}").strip()
    base_username = base_username.replace(" ", "").lower()
    username = base_username
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base_username}{suffix}"

    password = secrets.token_urlsafe(9)
    user = User.objects.create_user(
        username=username,
        email=vendor.email or "",
        password=password,
        first_name=vendor.name[:150] if vendor.name else "",
        last_name="(Vendor)",
    )
    user.is_staff = False
    user.is_active = True
    user.save()

    VendorAccount.objects.create(vendor=vendor, user=user, is_active=True)

    messages.success(
        request,
        f"Vendor login created. Username: {username} | Temporary password: {password}",
    )
    return redirect('user:control_panel_home')


@login_required
@user_passes_test(is_admin)
def control_panel_user_permissions(request, user_id):
    """
    Legacy URL (v2).

    Redirect to the new unified permission manager, pre-selecting this user.
    """
    u = get_object_or_404(User, id=user_id)
    if hasattr(u, "vendor_account"):
        category = "vendor"
    elif (
        getattr(u, "is_staff", False)
        and getattr(getattr(u, "profile", None), "department", None) == "Associate"
    ):
        category = "vendor"
    elif getattr(u, "is_staff", False):
        category = "staff"
    else:
        category = "customer"

    return redirect(f"{reverse('user:control_panel_permissions')}?category={category}&targets={u.id}")


@login_required
@user_passes_test(is_admin)
def control_panel_permissions(request):
    """
    Unified permission manager (v3):
    - choose category: staff/vendor/customer
    - select one or more targets
    - apply preset or custom portals/modules/operations
    """
    if not request.session.get("control_panel_authenticated"):
        messages.warning(request, "Please login to Control Panel first")
        return redirect("user:control_panel_login")

    # Lists for selection UI
    associate_staff_ids = list(
        User.objects.filter(is_active=True, is_staff=True, profile__department="Associate")
        .values_list("id", flat=True)
    )

    staff_users = (
        User.objects.filter(is_active=True, is_staff=True)
        .exclude(id__in=associate_staff_ids)
        .select_related("profile")
        .order_by("username")
    )
    customer_users = (
        User.objects.filter(is_active=True, is_staff=False, vendor_account__isnull=True)
        .select_related("profile")
        .order_by("username")
    )
    vendor_accounts_qs = (
        VendorAccount.objects.select_related("vendor", "user", "user__profile")
        .filter(is_active=True, user__is_active=True)
        .order_by("vendor__name", "user__username")
    )

    # Vendor category should show only true vendor-linked accounts.
    vendor_accounts = list(vendor_accounts_qs)

    # Vendor category targets: real vendor logins + Associate staff without a vendor login (same sidebar/dashboard CP UI).
    linked_vendor_user_ids = {va.user_id for va in vendor_accounts}
    vendor_permission_targets = []
    for va in vendor_accounts:
        v = va.vendor
        vid = (v.vendor_id or str(v.pk)).strip() if v else "—"
        vendor_permission_targets.append(
            {
                "user": va.user,
                "vendor_account": va,
                "vend_id": vid,
                "title": v.name if v else "",
                "is_associate_only": False,
            }
        )
    for u in (
        User.objects.filter(is_active=True, is_staff=True, profile__department="Associate")
        .exclude(id__in=linked_vendor_user_ids)
        .select_related("profile")
        .order_by("username")
    ):
        vendor_permission_targets.append(
            {
                "user": u,
                "vendor_account": None,
                "vend_id": "—",
                "title": f"Associate ({u.username})",
                "is_associate_only": True,
            }
        )

    # Ensure Complaint Dashboard and Stock Dashboard portals exist
    CPPortal.objects.get_or_create(
        name="complaint_dashboard",
        defaults={
            "display_name": "Complaint Dashboard",
            "order": 5,
            "is_active": True,
        }
    )
    CPPortal.objects.get_or_create(
        name="stock_dashboard",
        defaults={
            "display_name": "Stock Dashboard",
            "order": 6,
            "is_active": True,
        }
    )
    
    # Ensure newly introduced modules exist for existing databases too.
    module_seed = [
        ("employee", "Employee", 1),
        ("customer", "Customer", 2),
        ("quotation", "Quotation", 3),
        ("dashboard", "Dashboard", 4),
        ("product", "Product", 5),
        ("inventory", "Inventory", 6),
        ("transactions", "Transactions", 7),
        ("firereport", "Fire Report", 8),
        ("barcode", "Barcode", 9),
        ("services", "Services", 10),
    ]
    for m_name, m_display, m_order in module_seed:
        mod, _ = CPModule.objects.get_or_create(
            name=m_name,
            defaults={"display_name": m_display, "order": m_order, "is_active": True},
        )
        # Ensure all operation rows exist for each module.
        for op_idx, op in enumerate(OPERATIONS_ORDER, start=1):
            CPModulePermission.objects.get_or_create(
                module=mod,
                operation=op,
                defaults={"display_name": op.title(), "order": op_idx, "is_active": True},
            )

    portals = list(CPPortal.objects.filter(is_active=True).order_by("order", "display_name"))
    modules = list(CPModule.objects.filter(is_active=True).order_by("order", "display_name"))
    perm_qs = CPModulePermission.objects.filter(is_active=True, module__in=modules).select_related("module")
    perm_by_key = {f"{p.module.name}:{p.operation}": p for p in perm_qs}

    # Target selection
    def _parse_target_ids(raw_values):
        ids = []
        for raw in raw_values:
            if raw is None:
                continue
            for token in str(raw).split(","):
                token = token.strip()
                if token.isdigit():
                    ids.append(token)
        # preserve order while removing duplicates
        seen = set()
        out = []
        for i in ids:
            if i in seen:
                continue
            seen.add(i)
            out.append(i)
        return out

    selected_category = (request.GET.get("category") or request.POST.get("category") or "staff").lower()
    if request.method == "POST":
        selected_targets = _parse_target_ids(request.POST.getlist("targets"))
    else:
        get_target_values = request.GET.getlist("targets")
        # Backward-compatible fallback for old links using single "targets" / "target"
        if not get_target_values and request.GET.get("target"):
            get_target_values = [request.GET.get("target")]
        if not get_target_values and request.GET.get("targets"):
            get_target_values = [request.GET.get("targets")]
        selected_targets = _parse_target_ids(get_target_values)

    # First time open (per browser session): force a clean reset.
    # Requirement: user checkboxes + all portal/module/operation controls should be blank.
    first_open_blank = False
    if request.method == "GET":
        has_targets_in_url = bool(request.GET.get("targets") or request.GET.get("target"))
        if (not request.session.get("cp_perm_manager_initialized")) and (not has_targets_in_url):
            request.session["cp_perm_manager_initialized"] = True
            request.session.pop("cp_last_target_id", None)
            request.session.pop("cp_last_target_category", None)
            first_open_blank = True
            selected_targets = []

    # If manager is reopened without explicit targets, restore last selected target.
    # But if admin explicitly reset (unselect all), don't restore anything.
    if request.method == "GET" and request.GET.get("reset") == "1":
        request.session.pop("cp_last_target_id", None)
        request.session.pop("cp_last_target_category", None)
    elif not selected_targets and request.method == "GET" and not first_open_blank:
        last_id = request.session.get("cp_last_target_id")
        last_category = request.session.get("cp_last_target_category")
        if last_id and str(last_id).isdigit() and (not last_category or last_category == selected_category):
            selected_targets = [str(last_id)]

    selected_users = list(User.objects.filter(id__in=selected_targets).order_by("username"))
    is_bulk = len(selected_users) != 1
    single_user = selected_users[0] if len(selected_users) == 1 else None

    if single_user:
        request.session["cp_last_target_id"] = single_user.id
        request.session["cp_last_target_category"] = selected_category

    # Defaults / preset prefill
    preset_key = (request.GET.get("preset") or request.POST.get("preset") or "").strip() or "staff_standard"
    if first_open_blank and not preset_key:
        preset_key = "none"
    if selected_category == "vendor":
        preset_key = preset_key if preset_key != "staff_standard" else "vendor_standard"
    elif selected_category == "customer":
        preset_key = preset_key if preset_key != "staff_standard" else "customer_standard"
    preset = preset_by_key(preset_key)
    preset_portals, preset_perms_pairs = preset_checkbox_state(preset)
    preset_perms = {f"{m}:{op}" for (m, op) in preset_perms_pairs}

    # Ensure nav items (submodules) exist (safe idempotent upsert).
    # Keep this unconditional so newly added specs (e.g., Services) appear on existing databases.
    if portals:
        portal_by_name = {p.name: p for p in portals}
        for spec in all_nav_specs():
            portal = portal_by_name.get(spec.portal)
            if not portal:
                continue
            CPNavItem.objects.update_or_create(
                key=spec.key,
                defaults={
                    "portal": portal,
                    "section": spec.section,
                    "label": spec.label,
                    "url_name": spec.url_name,
                    "order": spec.order,
                    "is_active": True,
                },
            )

    nav_items = list(
        CPNavItem.objects.filter(is_active=True).select_related("portal").order_by("portal__order", "section", "order")
    )
    if selected_category == "vendor":
        nav_items = [
            ni
            for ni in nav_items
            if ni.key != NAV_KEY_HIDDEN_FOR_VENDOR_PERMISSIONS
        ]

    def _split_section(section: str):
        # "Project Details / Barcode" -> ("Project Details", "Barcode")
        parts = [p.strip() for p in (section or "").split("/", 1)]
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], parts[1]

    # Build a UI-friendly ordered tree: Module -> (optional subgroup) -> items
    nav_tree = []
    nav_tree_index = OrderedDict()
    for ni in nav_items:
        top, sub = _split_section(ni.section)
        top = top or "Other"
        sub = sub.strip()

        if top not in nav_tree_index:
            nav_tree_index[top] = OrderedDict()
        if sub not in nav_tree_index[top]:
            nav_tree_index[top][sub] = []
        nav_tree_index[top][sub].append(ni)

    for top, subgroups in nav_tree_index.items():
        nav_tree.append(
            {
                "name": top,
                "subgroups": [
                    {"name": (sub or ""), "items": items}
                    for sub, items in subgroups.items()
                ],
            }
        )

    # Current state for single user only
    current_portal_grants = {}
    current_perm_grants = {}
    current_nav_grants = set()
    if single_user:
        current_portal_grants = {
            a.portal.name: a.granted
            for a in CPUserPortalAccess.objects.filter(user=single_user).select_related("portal")
        }
        current_perm_grants = {
            f"{a.module_permission.module.name}:{a.module_permission.operation}": a.granted
            for a in CPUserModulePermission.objects.filter(user=single_user)
            .select_related("module_permission", "module_permission__module")
        }
        current_nav_grants = {
            a.nav_item.key
            for a in CPUserNavAccess.objects.filter(user=single_user, granted=True).select_related("nav_item")
        }

    # Save
    if request.method == "POST" and request.POST.get("do_save") == "1":
        if not selected_users:
            messages.error(request, "Please select at least one user/vendor/customer.")
            return redirect("user:control_panel_permissions")

        overwrite = request.POST.get("overwrite") == "1"

        # Parse desired portals/modules from POST (name-based, stable)
        desired_portals = {p.name for p in portals if request.POST.get(f"portal_{p.name}") == "on"}
        desired_perms = set()
        for m in modules:
            if m.name in CP_PM_TABLE_HIDDEN_MODULE_NAMES:
                continue
            for op in OPERATIONS_ORDER:
                key = f"perm_{m.name}_{op}"
                if request.POST.get(key) == "on":
                    desired_perms.add(f"{m.name}:{op}")

        # Parse desired submodules (nav items) from POST
        desired_nav_keys = {ni.key for ni in nav_items if request.POST.get(f"nav_{ni.key}") == "on"}

        # IMPORTANT:
        # Portal access must be controlled ONLY by the Portal Access checkboxes.
        # Previously we inferred portal access from selected nav/submodule items, which
        # could re-enable a dashboard (e.g., Staff) even if the admin unchecked it.

        # NOTE: Removed automatic addition of category portal (staff/vendor/customer)
        # Admin must explicitly select portals in the Portal Access section.
        # This allows fine-grained control, e.g., granting only Complaint Dashboard without Staff Dashboard.

        with transaction.atomic():
            for u in selected_users:
                # Portals
                # Save EXACTLY what admin selected in Portal Access.
                for p in portals:
                    granted = p.name in desired_portals
                    CPUserPortalAccess.objects.update_or_create(
                        user=u,
                        portal=p,
                        defaults={"granted": granted, "granted_by": request.user},
                    )

                # Module operations
                for m in modules:
                    if m.name in CP_PM_TABLE_HIDDEN_MODULE_NAMES:
                        continue
                    for op in OPERATIONS_ORDER:
                        mp = perm_by_key.get(f"{m.name}:{op}")
                        if not mp:
                            continue
                        if overwrite:
                            granted = f"{m.name}:{op}" in desired_perms
                            CPUserModulePermission.objects.update_or_create(
                                user=u,
                                module_permission=mp,
                                defaults={"granted": granted, "granted_by": request.user},
                            )
                        else:
                            if f"{m.name}:{op}" in desired_perms:
                                CPUserModulePermission.objects.update_or_create(
                                    user=u,
                                    module_permission=mp,
                                    defaults={"granted": True, "granted_by": request.user},
                                )

                # Submodule/page (nav) grants
                for ni in nav_items:
                    if overwrite:
                        granted = ni.key in desired_nav_keys
                        CPUserNavAccess.objects.update_or_create(
                            user=u,
                            nav_item=ni,
                            defaults={"granted": granted, "granted_by": request.user},
                        )
                    else:
                        if ni.key in desired_nav_keys:
                            CPUserNavAccess.objects.update_or_create(
                                user=u,
                                nav_item=ni,
                                defaults={"granted": True, "granted_by": request.user},
                            )

        messages.success(
            request,
            f"Permissions saved for {len(selected_users)} user(s).",
        )

        # Redirect back, preserving selection
        ids = ",".join(str(u.id) for u in selected_users)
        return redirect(f"{reverse('user:control_panel_permissions')}?category={selected_category}&targets={ids}")

    context = {
        "selected_category": selected_category,
        "staff_users": staff_users,
        "customer_users": customer_users,
        "vendor_accounts": vendor_accounts,
        "vendor_permission_targets": vendor_permission_targets,
        "selected_users": selected_users,
        "is_bulk": is_bulk,
        "single_user": single_user,
        "portals": portals,
        "modules": modules,
        "operations": OPERATIONS_ORDER,
        "perm_exists": list(perm_by_key.keys()),
        "current_portal_grants": current_portal_grants,
        "current_perm_grants": current_perm_grants,
        "nav_items": nav_items,
        "nav_tree": nav_tree,
        "current_nav_grants": current_nav_grants,
        "presets": PRESETS,
        "preset_key": preset.key,
        "preset_portals": preset_portals,
        "preset_perms": preset_perms,
    }
    return render(request, "user/control_panel_permissions_v3.html", context)
    # Check if user is authenticated for control panel
    if not request.session.get('control_panel_authenticated'):
        messages.warning(request, 'Please login to Control Panel first')
        return redirect('user:control_panel_login')
    
    user = get_object_or_404(User, id=user_id)
    
    # Get all modules with their permissions
    modules = CPModule.objects.filter(is_active=True).prefetch_related(
        'permissions'
    ).order_by('order', 'display_name')

    portals = CPPortal.objects.filter(is_active=True).order_by("order", "display_name")
    portal_modules = {
        pm.portal_id: []
        for pm in CPPortalModule.objects.select_related("portal", "module")
        .order_by("portal__order", "order", "module__order", "module__display_name")
        .all()
    }
    for pm in CPPortalModule.objects.select_related("portal", "module").order_by(
        "portal__order", "order", "module__order", "module__display_name"
    ):
        portal_modules.setdefault(pm.portal_id, []).append(pm.module)
    
    # Get existing user permissions
    existing_permissions = CPUserModulePermission.objects.filter(
        user=user
    ).select_related('module_permission', 'module_permission__module')
    
    # Create a dict for quick lookup: {module_permission_id: granted}
    permission_dict = {perm.module_permission_id: perm.granted for perm in existing_permissions}
    
    # Organize permissions by operation for easier template rendering
    # Create a structure: {module_id: {operation: {id: perm_id, granted: bool}}}
    module_permissions_organized = {}
    for module in modules:
        module_permissions_organized[module.id] = {}
        for perm in module.permissions.filter(is_active=True).order_by('order'):
            module_permissions_organized[module.id][perm.operation] = {
                'id': perm.id,
                'granted': permission_dict.get(perm.id, False)
            }
    
    if request.method == 'POST':
        # Save permissions
        with transaction.atomic():
            # Save portal access
            submitted_portals = set()
            for portal in portals:
                key = f"portal_{portal.id}"
                granted = key in request.POST
                CPUserPortalAccess.objects.update_or_create(
                    user=user,
                    portal=portal,
                    defaults={"granted": granted, "granted_by": request.user},
                )
                if granted:
                    submitted_portals.add(portal.id)

            # Get all submitted permissions
            submitted_permissions = {}
            for key, value in request.POST.items():
                if key.startswith('permission_'):
                    module_perm_id = int(key.replace('permission_', ''))
                    granted = value == 'true' or value == 'on'
                    submitted_permissions[module_perm_id] = granted
            
            # Update or create permissions
            for module in modules:
                for module_perm in module.permissions.filter(is_active=True):
                    module_perm_id = module_perm.id
                    granted = submitted_permissions.get(module_perm_id, False)
                    
                    # Update or create UserModulePermission
                    user_perm, created = CPUserModulePermission.objects.update_or_create(
                        user=user,
                        module_permission=module_perm,
                        defaults={
                            'granted': granted,
                            'granted_by': request.user,
                        }
                    )
            
            messages.success(request, f'Permissions updated successfully for {user.username}')
            return redirect('user:control_panel_user_permissions', user_id=user_id)

    portal_access = {
        a.portal_id: a.granted
        for a in CPUserPortalAccess.objects.filter(user=user).all()
    }
    
    context = {
        'selected_user': user,
        'modules': modules,
        'portals': portals,
        'portal_modules': portal_modules,
        'portal_access': portal_access,
        'permission_dict': permission_dict,
        'module_permissions_organized': module_permissions_organized,
    }
    
    return render(request, 'user/control_panel_user_permissions.html', context)


@login_required
@user_passes_test(is_admin)
def control_panel_update_password(request):
    """Update control panel password"""
    # Check if user is authenticated for control panel
    if not request.session.get('control_panel_authenticated'):
        messages.warning(request, 'Please login to Control Panel first')
        return redirect('user:control_panel_login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not all([current_password, new_password, confirm_password]):
            messages.error(request, 'All fields are required')
            return redirect('user:control_panel_update_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return redirect('user:control_panel_update_password')
        
        # Get control panel access
        access_config = ControlPanelAccess.objects.first()
        if not access_config:
            access_config = ControlPanelAccess.objects.create(
                password_hash=hashers.make_password(new_password),
                is_active=True
            )
            messages.success(request, 'Control Panel password set successfully')
            return redirect('user:control_panel_home')
        
        # Verify current password
        if not hashers.check_password(current_password, access_config.password_hash):
            messages.error(request, 'Current password is incorrect')
            return redirect('user:control_panel_update_password')
        
        # Update password
        access_config.password_hash = hashers.make_password(new_password)
        access_config.save()
        
        messages.success(request, 'Control Panel password updated successfully')
        return redirect('user:control_panel_home')
    
    return render(request, 'user/control_panel_update_password.html')


@login_required
@user_passes_test(is_admin)
def control_panel_logout(request):
    """Logout from control panel"""
    request.session.pop('control_panel_authenticated', None)
    request.session.pop('control_panel_authenticated_at', None)
    messages.success(request, 'Logged out from Control Panel')
    return redirect('user:control_panel_login')


@login_required
@user_passes_test(is_admin)
@require_POST
@csrf_protect
def control_panel_save_permissions(request, user_id):
    """AJAX endpoint to save permissions"""
    # Check if user is authenticated for control panel
    if not request.session.get('control_panel_authenticated'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        data = json.loads(request.body)
        permissions = data.get('permissions', {})
        
        with transaction.atomic():
            for module_perm_id, granted in permissions.items():
                try:
                    module_perm = CPModulePermission.objects.get(id=int(module_perm_id))
                    CPUserModulePermission.objects.update_or_create(
                        user=user,
                        module_permission=module_perm,
                        defaults={
                            'granted': bool(granted),
                            'granted_by': request.user,
                        }
                    )
                except (CPModulePermission.DoesNotExist, ValueError):
                    continue
        
        return JsonResponse({'success': True, 'message': 'Permissions saved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def initialize_modules_permissions(request):
    """Initialize default modules and permissions (one-time setup)"""
    # Check if user is authenticated for control panel
    if not request.session.get('control_panel_authenticated'):
        messages.warning(request, 'Please login to Control Panel first')
        return redirect('user:control_panel_login')
    
    if request.method == 'POST':
        # Define default modules
        default_modules = [
            {'name': 'employee', 'display_name': 'Employee', 'order': 1},
            {'name': 'customer', 'display_name': 'Customer', 'order': 2},
            {'name': 'quotation', 'display_name': 'Quotation', 'order': 3},
            {'name': 'dashboard', 'display_name': 'Dashboard', 'order': 4},
            {'name': 'product', 'display_name': 'Product', 'order': 5},
            {'name': 'inventory', 'display_name': 'Inventory', 'order': 6},
            {'name': 'transactions', 'display_name': 'Transactions', 'order': 7},
            {'name': 'firereport', 'display_name': 'Fire Report', 'order': 8},
            {'name': 'barcode', 'display_name': 'Barcode', 'order': 9},
            {'name': 'services', 'display_name': 'Services', 'order': 10},
        ]
        
        # Define default operations
        # NOTE: Keep in sync with control panel UI columns.
        default_operations = [
            {'operation': 'add', 'display_name': 'Add', 'order': 1},
            {'operation': 'view', 'display_name': 'View', 'order': 2},
            {'operation': 'edit', 'display_name': 'Edit', 'order': 3},
            {'operation': 'delete', 'display_name': 'Delete', 'order': 4},
            {'operation': 'export', 'display_name': 'Export', 'order': 5},
            {'operation': 'import', 'display_name': 'Import', 'order': 6},
            {'operation': 'approve', 'display_name': 'Approve', 'order': 7},
            {'operation': 'reject', 'display_name': 'Reject', 'order': 8},
        ]
        
        with transaction.atomic():
            # Create modules
            for module_data in default_modules:
                module, created = CPModule.objects.get_or_create(
                    name=module_data['name'],
                    defaults={
                        'display_name': module_data['display_name'],
                        'order': module_data['order'],
                        'is_active': True,
                    }
                )
                
                # Create permissions for each module
                for op_data in default_operations:
                    CPModulePermission.objects.get_or_create(
                        module=module,
                        operation=op_data['operation'],
                        defaults={
                            'display_name': op_data['display_name'],
                            'order': op_data['order'],
                            'is_active': True,
                        }
                    )

            # Create portals
            default_portals = [
                {"name": "admin", "display_name": "Admin Dashboard", "order": 1},
                {"name": "staff", "display_name": "Staff Dashboard", "order": 2},
                {"name": "customer", "display_name": "Customer Dashboard", "order": 3},
                {"name": "vendor", "display_name": "Vendor Dashboard", "order": 4},
                {"name": "complaint_dashboard", "display_name": "Complaint Dashboard", "order": 5},
                {"name": "stock_dashboard", "display_name": "Stock Dashboard", "order": 6},
            ]
            portals = {}
            for p in default_portals:
                portal, _ = CPPortal.objects.get_or_create(
                    name=p["name"],
                    defaults={
                        "display_name": p["display_name"],
                        "order": p["order"],
                        "is_active": True,
                    },
                )
                portals[p["name"]] = portal

            # Default portal -> module mapping (can be refined later)
            module_map = {m.name: m for m in CPModule.objects.all()}
            admin_modules = list(module_map.values())
            staff_modules = [m for m in module_map.values() if m.name != "employee"]
            customer_modules = [module_map.get(n) for n in ["customer", "firereport", "barcode", "dashboard"] if module_map.get(n)]
            vendor_modules = [module_map.get(n) for n in ["transactions", "product", "inventory"] if module_map.get(n)]

            for order, m in enumerate(admin_modules, start=1):
                CPPortalModule.objects.get_or_create(portal=portals["admin"], module=m, defaults={"order": order})
            for order, m in enumerate(staff_modules, start=1):
                CPPortalModule.objects.get_or_create(portal=portals["staff"], module=m, defaults={"order": order})
            for order, m in enumerate(customer_modules, start=1):
                CPPortalModule.objects.get_or_create(portal=portals["customer"], module=m, defaults={"order": order})
            for order, m in enumerate(vendor_modules, start=1):
                CPPortalModule.objects.get_or_create(portal=portals["vendor"], module=m, defaults={"order": order})

            # Create/refresh nav items (submodules) registry
            for spec in all_nav_specs():
                portal = portals.get(spec.portal)
                if not portal:
                    continue
                CPNavItem.objects.update_or_create(
                    key=spec.key,
                    defaults={
                        "portal": portal,
                        "section": spec.section,
                        "label": spec.label,
                        "url_name": spec.url_name,
                        "order": spec.order,
                        "is_active": True,
                    },
                )
        
        messages.success(request, 'Modules and permissions initialized successfully')
        return redirect('user:control_panel_home')
    
    return render(request, 'user/control_panel_initialize.html')
