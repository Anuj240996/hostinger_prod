from django.utils.deprecation import MiddlewareMixin
from .models import Organization, UserProfile
from .utils import set_current_organization

# class OrganizationMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         # Determine organization from subdomain or user profile
#         org = None
#
#         # Option 1: From subdomain (e.g., company1.localhost:8000)
#         host = request.get_host().split(':')[0]
#         subdomain = host.split('.')[0] if '.' in host else None
#         if subdomain:
#             try:
#                 org = Organization.objects.get(subdomain=subdomain)
#             except Organization.DoesNotExist:
#                 pass
#
#         # Option 2: From authenticated user's profile
#         if not org and request.user.is_authenticated:
#             try:
#                 org = request.user.core_profile.organization
#             except (UserProfile.DoesNotExist, AttributeError):
#                 pass
#
#         # Store in thread-local for use in models
#         set_current_organization(org)
#         # Also attach to request for convenience
#         request.organization = org
#
#     def process_response(self, request, response):
#         # Clean up thread-local after request
#         from .utils import clear_current_organization
#         clear_current_organization()
#         return response


from django.utils.deprecation import MiddlewareMixin
from .models import Organization, UserProfile
from .utils import set_current_organization

class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        org = None

        # 1. Subdomain detection
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0] if '.' in host else None
        if subdomain:
            try:
                org = Organization.objects.get(subdomain=subdomain)
            except Organization.DoesNotExist:
                pass

        # 2. Authenticated user's profile
        if not org and request.user.is_authenticated:
            try:
                org = request.user.core_profile.organization
            except (UserProfile.DoesNotExist, AttributeError):
                pass

        # 3. Platform admin session override (if they have permission)
        if request.user.is_authenticated and request.user.has_perm('core.view_all_organizations_data'):
            selected_org_id = request.session.get('selected_org_id')
            if selected_org_id:
                try:
                    org = Organization.objects.get(id=selected_org_id)
                except Organization.DoesNotExist:
                    # remove invalid session
                    request.session.pop('selected_org_id', None)

        set_current_organization(org)
        request.organization = org

    def process_response(self, request, response):
        from .utils import clear_current_organization
        clear_current_organization()
        return response
