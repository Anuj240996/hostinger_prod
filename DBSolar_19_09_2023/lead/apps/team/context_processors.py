from apps.team.permissions import is_organization_admin

def org_admin_check(request):
    if request.user.is_authenticated and hasattr(request, 'organization') and request.organization:
        return {'user_is_org_admin': is_organization_admin(request.user, request.organization)}
    return {'user_is_org_admin': False}