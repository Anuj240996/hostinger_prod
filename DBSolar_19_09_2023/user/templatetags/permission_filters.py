"""
Template tags for checking module permissions
"""
from django import template
from user.permissions import has_cp_module_view, has_cp_operation, has_portal_access, has_nav_url_access

register = template.Library()


@register.filter(name='has_module_permission')
def has_module_permission(user, module_name):
    """
    Check if user has view permission for a module.
    Usage: {% if user|has_module_permission:"employee" %}
    """
    try:
        return has_cp_module_view(user, module_name)
    except Exception:
        return False


@register.filter(name='has_module_operation')
def has_module_operation(user, permission_string):
    """
    Check if user has a specific operation permission for a module.
    Usage: {% if user|has_module_operation:"employee:add" %}
    Format: "module_name:operation"
    """
    try:
        parts = permission_string.split(':')
        if len(parts) != 2:
            return False
        
        module_name, operation = parts

        return has_cp_operation(user, module_name, operation)
    except Exception:
        return False


@register.filter(name="has_portal_access")
def has_portal_access_filter(user, portal_name: str):
    """
    Check if user has access to a portal/dashboard.
    Usage: {% if user|has_portal_access:"vendor" %}
    """
    try:
        return has_portal_access(user, portal_name)
    except Exception:
        return False


@register.filter(name="is_associate_staff")
def is_associate_staff_filter(user):
    """
    True for staff users with Profile.department == 'Associate'.
    Usage: {% if user|is_associate_staff %}
    """
    try:
        from customer.staff_access import is_associate_staff

        return is_associate_staff(user)
    except Exception:
        return False


@register.filter(name="has_url_permission")
def has_url_permission_filter(user, url_name: str):
    """
    Check if user has access to a specific url_name/menu submodule.
    Usage: {% if user|has_url_permission:"customer-view_all_cust" %}
    """
    try:
        return has_nav_url_access(user, url_name)
    except Exception:
        return False
