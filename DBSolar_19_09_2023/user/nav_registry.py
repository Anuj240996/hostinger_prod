from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Set


# Staff sidebar "Dashboard" submenu: these CP nav keys follow Portal Access (same matrix as base.html).
DASHBOARD_NAV_KEYS: frozenset = frozenset(
    {
        "staff.dashboard.staff",
        "staff.dashboard.consumer",
        "staff.dashboard.complaint",
        "staff.dashboard.stock",
    }
)

# Permissions Manager (Vendor category): do not offer Staff Dashboard under Models & Sub-models.
NAV_KEY_HIDDEN_FOR_VENDOR_PERMISSIONS = "staff.dashboard.staff"

# Which dashboard nav keys are granted when each portal is enabled (Control Panel → Portal access).
PORTAL_TO_DASHBOARD_NAV_KEYS = {
    "staff": (
        "staff.dashboard.staff",
        "staff.dashboard.complaint",
        "staff.dashboard.stock",
    ),
    "customer": (
        "staff.dashboard.consumer",
        "staff.dashboard.complaint",
    ),
    "complaint_dashboard": ("staff.dashboard.complaint",),
    "stock_dashboard": ("staff.dashboard.stock",),
}


def nav_keys_for_granted_portals(portal_names: Iterable[str]) -> Set[str]:
    """Union of dashboard nav keys implied by the given portal names."""
    out: Set[str] = set()
    for name in portal_names:
        out.update(PORTAL_TO_DASHBOARD_NAV_KEYS.get(name, ()))
    return out


@dataclass(frozen=True)
class NavSpec:
    key: str
    portal: str
    section: str
    label: str
    url_name: str = ""
    order: int = 0


def staff_nav_specs() -> List[NavSpec]:
    """
    Staff portal menu structure, based on the list provided by the user.
    Keys are stable identifiers stored in DB, url_name matches Django url_name.
    """
    i = 0
    def n(key: str, section: str, label: str, url_name: str = "") -> NavSpec:
        nonlocal i
        i += 1
        return NavSpec(key=key, portal="staff", section=section, label=label, url_name=url_name, order=i)

    specs: List[NavSpec] = []

    # Dashboard
    specs += [
        n("staff.dashboard.staff", "Dashboard", "Staff Dashboard", "dashboard-index1"),
        n("staff.dashboard.consumer", "Dashboard", "Consumer Dashboard", "customer-view_all"),
        n("staff.dashboard.complaint", "Dashboard", "Complaint Dashboard", "firereport-dashboard"),
        n("staff.dashboard.stock", "Dashboard", "Stock Dashboard", "home"),
    ]

    # My Profile
    specs += [
        n("staff.profile.view", "My Profile", "View Profile", "user-profile"),
        n("staff.profile.edit", "My Profile", "Update Profile", "user-edit_profile"),
    ]

    # Employee
    specs += [
        n("staff.employee.add", "Employee", "Add Employee", "user-add"),
        n("staff.employee.list", "Employee", "Employee List", "dashboard-customers"),
    ]

    # Quotation
    specs += [
        n("staff.quotation.new", "Quotation", "New Quotation", "quotation:create_quotation"),
        n("staff.quotation.list", "Quotation", "Quotation List", "quotation:quotation_list"),
    ]

    # Consumer
    specs += [
        n("staff.customer.add", "Consumer", "Add Consumer", "customer-cust"),
        n("staff.customer.list", "Consumer", "Consumer List", "customer-view_all_cust"),
        n("staff.customer.update_name", "Consumer", "Update Consumer Name", "customer-update_company_name"),
        n("staff.customer.reassign", "Consumer", "Re-Assign Employee", "customer-change_staff"),
        n("staff.customer.search_staff", "Consumer", "Cons. SearchBy Staff", "customer-search_by_staff"),
    ]

    # Project Details -> Barcode
    specs += [
        n("staff.project.promote", "Project Details / Barcode", "Promote Barcode", "promote_page"),
        n("staff.project.solar_panel", "Project Details / Barcode", "Solar Module Panel", "detect_barcodes-detect_barcodes"),
        n("staff.project.inverter", "Project Details / Barcode", "Inverter", "detect_barcodes-detect_inverter"),
        n("staff.project.search", "Project Details / Barcode", "Search", "detect_barcodes-search_results"),
        n("staff.project.generate", "Project Details / Barcode", "Generate Barcode", "generate_barcodes-generate_barcodes"),
        n("staff.project.delete_barcode", "Project Details / Barcode", "Delete Barcode", "detect_barcodes-delete_barcode"),
    ]

    # Project Details -> Solar Pump
    specs += [
        n("staff.project.solar_pump", "Project Details / Solar Pump", "Solar Pump", "solar_pump_entry"),
        n("staff.project.controller", "Project Details / Solar Pump", "Controller", "controller_entry"),
    ]

    # Project Details -> Net Meters Details
    specs += [
        n("staff.project.meters.add", "Project Details / Net Meters", "Add Meters Details", "customer-meters"),
        n("staff.project.meters.display", "Project Details / Net Meters", "Display Meters Details", "customer-display_meters"),
        n("staff.project.meters.search", "Project Details / Net Meters", "Search", "customer-search_results"),
        n("staff.project.meters.delete", "Project Details / Net Meters", "Delete Meters", "customer-edit_meters"),
    ]

    # Project Details -> MSEB Records
    specs += [
        n("staff.project.mseb", "Project Details / MSEB", "MSEB Electricity Meters", "customer-MSEB"),
        n("staff.project.mseb.complete", "Project Details / MSEB", "Complete MSEB Details", "customer-complete_MSEB"),
        n("staff.project.mseb.update", "Project Details / MSEB", "Update MSEB Details", "customer-Update_MSEB"),
    ]

    # Project Details -> Site Inspection
    specs += [
        n("staff.project.site.enter", "Project Details / Site Inspection", "Enter Inspection Report", "customer-Site_Inspection_Details"),
        n("staff.project.site.display", "Project Details / Site Inspection", "Display Inspection Reports", "customer-display_Site_Inspection"),
    ]

    # Store Keeping -> Supplier
    specs += [
        n("staff.store.supplier.add_field", "Store Keeping / Supplier", "Add Field", "product_add_category"),
        n("staff.store.supplier.add", "Store Keeping / Supplier", "Add New Supplier", "new-supplier"),
        n("staff.store.supplier.list", "Store Keeping / Supplier", "Supplier List", "suppliers-list"),
    ]

    # Store Keeping -> Vendor
    specs += [
        n("staff.store.vendor.add", "Store Keeping / Vendor", "Add New Vendor", "new-vendor"),
        n("staff.store.vendor.list", "Store Keeping / Vendor", "Vendor List", "vendor-list"),
    ]

    # Store Keeping -> Favourite
    specs += [
        n("staff.store.favorite.create", "Store Keeping / Favourite", "Create Favourite", "favorite"),
        n("staff.store.favorite.list", "Store Keeping / Favourite", "Favourite List", "favorite_list_view"),
    ]

    # Store Keeping -> Inventory / Purchase / Sale / Final / Return
    specs += [
        n("staff.store.inventory.list", "Store Keeping / Inventory", "Inventory List", "inventory"),
        n("staff.store.purchase.new", "Store Keeping / Purchase", "New Incoming Stock", "select-supplier"),
        n("staff.store.purchase.list", "Store Keeping / Purchase", "Purchase List", "purchases-list"),
        n("staff.store.sale.new", "Store Keeping / Sale", "New Outgoing Stock", "select_customer"),
        n("staff.store.sale.list", "Store Keeping / Sale", "Sales Order List", "sales-list"),
        n("staff.store.finalsales.new", "Store Keeping / Final Sales DC", "Generate Final Sale DC", "merge_sales_bill"),
        n("staff.store.finalsales.list", "Store Keeping / Final Sales DC", "Final Sales List", "finalsales-list"),
        n("staff.store.returnsale.new", "Store Keeping / Return Sale DC", "Generate Return Sale DC", "return_select_customer"),
        n("staff.store.returnsale.list", "Store Keeping / Return Sale DC", "Return Sale List", "returnsales-list"),
        n("staff.store.search_serial", "Store Keeping", "Search Serial No.", "search_serial"),
    ]

    # Complaint
    specs += [
        n("staff.complaint.new", "Complaint", "New Request", "firereport-newRequest"),
        n("staff.complaint.assigned", "Complaint", "Assigned Request", "firereport-assignRequest"),
        n("staff.complaint.ontheway", "Complaint", "In Progress", "firereport-teamontheway"),
        n("staff.complaint.work", "Complaint", "Work In Progress", "firereport-workinprogress"),
        n("staff.complaint.complete", "Complaint", "Completed Request", "firereport-completeRequest"),
        n("staff.complaint.all", "Complaint", "All Request", "firereport-allRequest"),
        n("staff.complaint.reassign", "Complaint", "Re-Assign Request", "firereport-reassignRequest"),
        n("staff.complaint.report", "Complaint", "All Report", "firereport-dateReport"),
        n("staff.complaint.search", "Complaint", "Search", "firereport-search"),
    ]

    # Services
    specs += [
        n("staff.services.assigned", "Services", "Assigned Request", "firereport-service-assigned"),
        n("staff.services.in_process", "Services", "Requests In Process", "firereport-service-in-process"),
        n("staff.services.completed", "Services", "Completed Requests", "firereport-service-completed"),
    ]

    # New Task
    specs += [n("staff.task", "New Task", "New Task", "firereport-task")]

    # Report
    specs += [
        n("staff.report.barcode_print", "Report", "Barcode Print", "detect_barcodes-search"),
        n("staff.report.employee_list", "Report", "Employee List", "edit_pdf"),
        n("staff.report.consumer_list", "Report", "Consumer List", "customer-consumer_list"),
    ]

    # Notification
    specs += [
        n("staff.notify.view", "Notification", "View Notification", "dashboard-notification"),
        n("staff.notify.send_staff", "Notification", "Send Staff Notification", "dashboard-staff_Send_Notification"),
        n("staff.notify.send_consumer", "Notification", "Send Consumer Notification", "dashboard-consumer_Send_Notification"),
    ]

    # Change Password / Logout
    specs += [
        n("staff.change_password", "Account", "Change Password", "firereport-changePassword"),
        n("staff.logout", "Account", "Logout", "user-logout"),
    ]

    return specs


def all_nav_specs() -> List[NavSpec]:
    # For now only staff is defined; vendor/customer can be added similarly.
    return staff_nav_specs()

