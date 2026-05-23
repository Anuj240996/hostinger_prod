from django import template
from apps.team.permissions import is_organization_admin

register = template.Library()

@register.simple_tag(takes_context=True)
def user_is_org_admin(context):
    request = context['request']
    if request.user.is_authenticated and hasattr(request, 'organization') and request.organization:
        return is_organization_admin(request.user, request.organization)
    return False

