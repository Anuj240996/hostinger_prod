from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin

from apps.control_panel.models import UserRole


def is_organization_admin(user, organization):
    """Return True if user is an admin of the given organization."""
    if not user.is_authenticated:
        return False
    # Superusers are not automatically admins; they need the flag in their profile.
    return (hasattr(user, 'core_profile') and
            user.core_profile.organization == organization and
            user.core_profile.is_tenant_admin)

class OrganizationAdminRequiredMixin(AccessMixin):
    """Verify that the current user is an admin of the organization."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not is_organization_admin(request.user, request.organization):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def user_has_permission(user, permission_codename, organization=None):
    """Check if a user has a given permission (via roles) in the organization."""
    if user.is_superuser:
        return True
    if not organization and hasattr(user, 'core_profile'):
        organization = user.core_profile.organization
    if not organization:
        return False
    return UserRole.objects.filter(
        user=user,
        organization=organization,
        role__permissions__codename=permission_codename
    ).exists()
