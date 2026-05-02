"""
Maps URL names to required Control Panel permissions.

This intentionally covers only the core CRUD operations that match your
Control Panel checkboxes: add/view/edit/delete/export.

If a URL is not mapped, it is not blocked by CPPermissionMiddleware.
"""

from __future__ import annotations

from typing import Optional, Tuple

from django.http import HttpRequest

Permission = Tuple[str, str]  # (module_name, operation)


PORTAL_URLS = {
    # url_name: portal_name
    "dashboard-index": "admin",
    "dashboard-index1": "staff",
    "customer-view_all": "customer",
    "vendor-dashboard": "vendor",
    # vendor portal landing will be added later (vendor-portal todo)
}

# URL is allowed if the user has ANY of these portals (see Control Panel portal matrix).
PORTAL_URLS_ANY = {
    "home": ("staff", "stock_dashboard"),  # stock dashboard
    "firereport-dashboard": ("staff", "customer", "complaint_dashboard"),
}

# Sidebar / CP submodule url_names for the four Dashboard entries (portal + nav sync).
DASHBOARD_SUBMODULE_URL_NAMES = frozenset(
    {"dashboard-index1", "customer-view_all", "firereport-dashboard", "home"}
)


def required_permission(url_name: Optional[str], request: HttpRequest) -> Optional[Permission]:
    """
    Return (module, operation) required for the resolved url_name.
    """
    if not url_name:
        return None

    method = (request.method or "GET").upper()

    # CUSTOMER
    if url_name in {
        "customer-index",
        "customer-view_all",
        "customer-view_all_cust",
        "customer-display_meters",
        "customer-display_Site_Inspection",
        "customer-Cust_search",
        "customer-search_by_staff",
        "customer-search_results",
        "customer-consumer_list",
    }:
        return ("customer", "view")

    if url_name in {
        "customer-cust",
        "customer-Cust_emp",
        "customer-Comm_Cust",
        "customer-Comp_Cust",
        "customer-Govt_Cust",
        "customer-add_meter",
        "customer-meters",
        "customer-Site_Technical_Details",
        "customer-Site_Inspection_Details",
        "solar_pump_entry",
        "controller_entry",
    }:
        return ("customer", "add")

    if url_name in {
        "customer-customer-update",
        "customer-customer-updatepage",
        "customer-edit_meters",
        "customer-Update_MSEB",
        "customer-update_company_name",
        "customer-change_staff",
        "customer-save_change_staff",
        "update_solar_pump",
        "update_controller",
    }:
        return ("customer", "edit")

    if url_name in {
        "delete_solar_pump_records",
        "delete_controller_records",
    }:
        return ("customer", "delete")

    # TRANSACTIONS (suppliers/vendors/purchase/sales)
    if url_name in {
        "suppliers-list",
        "vendor-list",
        "purchases-list",
        "sales-list",
        "finalsales-list",
        "returnsales-list",
        "supplier-detail",
        "vendor-detail",
        "search_serial",
    }:
        return ("transactions", "view")

    if url_name in {
        "new-supplier",
        "new-vendor",
        "new-purchase",
        "new-sale",
        "new-sale_bill",
        "new-sale1",
        "select-supplier",
        "select_customer",
        "select_customer_bill",
    }:
        return ("transactions", "add")

    if url_name in {
        "edit-supplier",
        "edit-vendor",
        "purchase_edit",
        "edit_sale",
        "edit_final_sale",
        "return_edit",
        "finalsales_return_edit",
        "update_purchase_serial_numbers",
        "update_sales_billno",
    }:
        return ("transactions", "edit")

    if url_name in {
        "delete-supplier",
        "delete-vendor",
        "delete-purchase",
        "delete-sale",
        "delete-final-sale",
    }:
        return ("transactions", "delete")

    # PRODUCT
    if url_name in {"product_add_category"}:
        # This view mixes listing and create based on POST payload.
        return ("product", "add") if method == "POST" else ("product", "view")

    if url_name in {"edit_category", "update_subcategory", "update_product", "update_supplier"}:
        return ("product", "edit")

    if url_name in {"delete_category", "delete_subcategory", "delete_product", "delete_brand", "delete_unit", "delete_supplier"}:
        return ("product", "delete")

    # INVENTORY
    if url_name in {"inventory", "favorite", "favorite_list_view"}:
        return ("inventory", "view")

    if url_name in {"new-stock", "create_favorite_list"}:
        return ("inventory", "add")

    if url_name in {"edit-stock", "edit_favorite_list"}:
        return ("inventory", "edit")

    if url_name in {"delete-stock", "delete_favorite_list"}:
        return ("inventory", "delete")

    # QUOTATION
    if url_name in {"quotation_list"}:
        return ("quotation", "view")
    if url_name in {"create_quotation"}:
        return ("quotation", "add")
    if url_name in {"edit_quotation", "revise_quotation"}:
        return ("quotation", "edit")

    # FIREREPORT
    if url_name in {
        "firereport-viewStatus",
        "firereport-newRequest",
        "firereport-assignRequest",
        "firereport-teamontheway",
        "firereport-workinprogress",
        "firereport-completeRequest",
        "firereport-allRequest",
        "firereport-manageTeam",
        "firereport-search",
        "firereport-dateReport",
    }:
        return ("firereport", "view")

    if url_name in {"firereport-reporting", "firereport-task", "firereport-addTeam"}:
        return ("firereport", "add")

    if url_name in {"firereport-editTeam", "firereport-viewRequestDetails", "firereport-reviewRequestDetails"}:
        return ("firereport", "edit")

    if url_name in {"firereport-deleteTeam", "firereport-deleteRequest"}:
        return ("firereport", "delete")

    # SERVICES
    if url_name in {
        "firereport-service-assigned",
        "firereport-service-in-process",
        "firereport-service-completed",
        "firereport-service-viewRequestDetails",
    }:
        return ("firereport", "view")
    if url_name in {"firereport-service-mark-in-process", "firereport-service-mark-completed"}:
        return ("firereport", "edit")

    # BARCODE / detect_barcodes
    if url_name.startswith("detect_barcodes-") or url_name.startswith("generate_barcodes-"):
        # Most barcode pages are view/search workflows; uploads/edits are still treated as add/edit.
        if url_name in {"detect_barcodes-edit_barcode"}:
            return ("barcode", "edit")
        if url_name in {"detect_barcodes-delete_barcode"}:
            return ("barcode", "delete")
        return ("barcode", "view")

    # DASHBOARD
    if url_name in {"dashboard-index", "dashboard-index1"}:
        return ("dashboard", "view")

    return None

