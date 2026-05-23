from apps.control_panel.models import UserRole


def has_permission(user, permission_codename, organization=None):
    # Superuser bypass
    if user.is_superuser:
        return True
    # Get user's roles in the organization (from request.organization)
    if not organization and hasattr(user, 'profile'):
        organization = user.profile.organization
    if not organization:
        return False
    return UserRole.objects.filter(
        user=user,
        organization=organization,
        role__permissions__codename=permission_codename
    ).exists()