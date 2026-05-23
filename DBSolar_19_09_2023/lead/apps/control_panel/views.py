# # from django.shortcuts import render
# # from django.contrib.admin.views.decorators import staff_member_required
# # from django.contrib.auth.models import User
# # from apps.core.models import Organization, UserProfile
# # from .models import SubscriptionPlan, OrganizationSubscription, Feature, Role
# # from django.shortcuts import render
# # from django.contrib.admin.views.decorators import staff_member_required
# # from django.contrib.auth.models import User
# # from apps.core.models import Organization, UserProfile
# # from .models import SubscriptionPlan, OrganizationSubscription, Feature, Role
# #
# # @staff_member_required
# # def dashboard(request):
# #     # Only superusers can access the full control panel
# #     if not request.user.is_superuser:
# #         return render(request, 'control_panel/access_denied.html')
# #
# #     context = {
# #         'total_orgs': Organization.objects.count(),
# #         'active_orgs': Organization.objects.filter(is_active=True).count(),
# #         'suspended_orgs': Organization.objects.filter(is_active=False, suspended_at__isnull=False).count(),
# #         'total_users': User.objects.count(),
# #         'users_with_profile': UserProfile.objects.count(),
# #         'total_plans': SubscriptionPlan.objects.count(),
# #         'active_plans': SubscriptionPlan.objects.filter(is_active=True).count(),
# #         'total_features': Feature.objects.count(),
# #         'total_roles': Role.objects.count(),
# #         'recent_orgs': Organization.objects.order_by('-created_at')[:5],
# #         'recent_users': User.objects.order_by('-date_joined')[:5],
# #     }
# #     return render(request, 'control_panel/dashboard.html', context)
#
# from django.shortcuts import render
# from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.auth.models import User
# from apps.core.models import Organization, UserProfile
# from .models import SubscriptionPlan, OrganizationSubscription, Feature, Role, OrganizationFeature
#
#
# @staff_member_required
# def dashboard(request):
#     # Only superusers can access the full control panel
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     context = {
#         'total_orgs': Organization.objects.count(),
#         'active_orgs': Organization.objects.filter(is_active=True).count(),
#         'suspended_orgs': Organization.objects.filter(is_active=False, suspended_at__isnull=False).count(),
#         'total_users': User.objects.count(),
#         'users_with_profile': UserProfile.objects.count(),
#         'total_plans': SubscriptionPlan.objects.count(),
#         'active_plans': SubscriptionPlan.objects.filter(is_active=True).count(),
#         'total_features': Feature.objects.count(),
#         'total_roles': Role.objects.count(),
#         'recent_orgs': Organization.objects.order_by('-created_at')[:5],
#         'recent_users': User.objects.order_by('-date_joined')[:5],
#     }
#     return render(request, 'control_panel/dashboard.html', context)
#
# @staff_member_required
# def organizations(request):
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     orgs = Organization.objects.all().order_by('-created_at')
#     return render(request, 'control_panel/organizations_list.html', {'organizations': orgs})
#
# @staff_member_required
# def users(request):
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     users = User.objects.all().select_related('core_profile__organization').order_by('-date_joined')
#     return render(request, 'control_panel/users_list.html', {'users': users})
#
# @staff_member_required
# def roles(request):
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     roles = Role.objects.all().select_related('organization').order_by('name')
#     return render(request, 'control_panel/roles_list.html', {'roles': roles})
#
# @staff_member_required
# def subscriptions(request):
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     subs = OrganizationSubscription.objects.all().select_related('organization', 'plan').order_by('-start_date')
#     plans = SubscriptionPlan.objects.all()
#     return render(request, 'control_panel/subscriptions_list.html', {'subscriptions': subs, 'plans': plans})
#
# @staff_member_required
# def feature_flags(request):
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     features = Feature.objects.all()
#     org_features = OrganizationFeature.objects.all().select_related('organization', 'feature')
#     return render(request, 'control_panel/feature_flags_list.html', {'features': features, 'org_features': org_features})


from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .mixins import SuperuserRequiredMixin
from apps.core.models import Organization, UserProfile
from .models import Role, Feature, OrganizationFeature, SubscriptionPlan, OrganizationSubscription
from .forms import (
    OrganizationForm, UserForm, UserProfileForm, RoleForm,
    FeatureForm, OrganizationFeatureForm, SubscriptionPlanForm,
    OrganizationSubscriptionForm
)
from django.views.generic import ListView
from .models import AuditLog
from django.http import JsonResponse
from .models import Role, Permission

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import OrganizationLimitsForm


from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from apps.core.models import Organization
from ..leads.models import Lead
from ..quotations.models import Quotation


@permission_required('core.view_all_organizations_data')
def switch_organization(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    request.session['selected_org_id'] = org.id
    # Redirect back to the page they came from, or to platform dashboard
    next_url = request.GET.get('next', reverse('control_panel:dashboard'))
    return redirect(next_url)

@permission_required('core.view_all_organizations_data')
def clear_organization_context(request):
    request.session.pop('selected_org_id', None)
    return redirect('control_panel:dashboard')



# ---------- Dashboard ----------
# def dashboard(request):
#     if not request.user.is_superuser:
#         return render(request, 'control_panel/access_denied.html')
#     context = {
#         'total_orgs': Organization.objects.count(),
#         'active_orgs': Organization.objects.filter(is_active=True).count(),
#         'total_users': User.objects.count(),
#         'users_with_profile': UserProfile.objects.count(),
#         'total_plans': SubscriptionPlan.objects.count(),
#         'active_plans': SubscriptionPlan.objects.filter(is_active=True).count(),
#         'total_features': Feature.objects.count(),
#         'total_roles': Role.objects.count(),
#         'recent_orgs': Organization.objects.order_by('-created_at')[:5],
#         'recent_users': User.objects.order_by('-date_joined')[:5],
#     }
#     return render(request, 'control_panel/dashboard.html', context)

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
# from apps.core.models import Organization, User, Lead, Quotation  # adjust imports as needed
from .models import SubscriptionPlan, OrganizationSubscription
#
# @permission_required('core.view_platform_dashboard')
# def dashboard(request):
#     # Get selected organization from session (if any)
#     selected_org_id = request.session.get('selected_org_id')
#     selected_org = None
#     if selected_org_id:
#         try:
#             selected_org = Organization.objects.get(id=selected_org_id)
#         except Organization.DoesNotExist:
#             selected_org_id = None
#             request.session.pop('selected_org_id', None)
#
#     # Base querysets
#     orgs_qs = Organization.objects.all()
#     users_qs = User.objects.all()
#     leads_qs = Lead.objects.all()
#     quotations_qs = Quotation.objects.all()
#     subs_qs = OrganizationSubscription.objects.all()
#
#     if selected_org:
#         # Filter to selected organization
#         orgs_qs = orgs_qs.filter(id=selected_org.id)
#         users_qs = users_qs.filter(core_profile__organization=selected_org)
#         leads_qs = leads_qs.filter(organization=selected_org)
#         quotations_qs = quotations_qs.filter(organization=selected_org)
#         subs_qs = subs_qs.filter(organization=selected_org)
#
#     # KPIs
#     total_orgs = orgs_qs.count()
#     active_orgs = orgs_qs.filter(is_active=True).count()
#     suspended_orgs = orgs_qs.filter(is_active=False).count()
#     total_users = users_qs.count()
#     total_leads = leads_qs.count()
#     total_quotations = quotations_qs.count()
#
#     # Revenue (sum of active subscription plan monthly prices)
#     total_revenue = subs_qs.filter(
#         status='active'
#     ).aggregate(total=Sum('plan__monthly_price'))['total'] or 0
#
#     # Subscriptions expiring soon (next 7 days) – always show platform-wide? Or filter? We'll show only relevant ones.
#     expiring_soon = OrganizationSubscription.objects.filter(
#         end_date__lte=timezone.now().date() + timedelta(days=7),
#         status='active'
#     ).select_related('organization', 'plan')
#     if selected_org:
#         expiring_soon = expiring_soon.filter(organization=selected_org)
#
#     # Heatmap data (leads with coordinates)
#     leads_with_coords = leads_qs.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
#     heatmap_points = [[float(l.latitude), float(l.longitude), 1] for l in leads_with_coords]
#
#     # All organizations for the dropdown
#     all_orgs = Organization.objects.all().order_by('legal_name')
#
#     # Recent organizations (platform-wide or filtered)
#     recent_orgs = orgs_qs.order_by('-created_at')[:5]
#
#     context = {
#         'selected_org': selected_org,
#         'total_orgs': total_orgs,
#         'active_orgs': active_orgs,
#         'suspended_orgs': suspended_orgs,
#         'total_users': total_users,
#         'total_leads': total_leads,
#         'total_quotations': total_quotations,
#         'total_revenue': total_revenue,
#         'expiring_soon': expiring_soon,
#         'organizations': all_orgs,
#         'recent_orgs': recent_orgs,
#         'heatmap_points': heatmap_points,
#     }
#     return render(request, 'control_panel/dashboard.html', context)
#
# from django.contrib.auth.decorators import permission_required
# from django.shortcuts import render
# from django.utils import timezone
# from datetime import timedelta
# from django.db.models import Sum, Count
# from .models import SubscriptionPlan, OrganizationSubscription
#
# @permission_required('core.view_platform_dashboard')
# def dashboard(request):
#     # Get selected organization from session (if any)
#     selected_org_id = request.session.get('selected_org_id')
#     selected_org = None
#     if selected_org_id:
#         try:
#             selected_org = Organization.objects.get(id=selected_org_id)
#         except Organization.DoesNotExist:
#             selected_org_id = None
#             request.session.pop('selected_org_id', None)
#
#     # Base querysets
#     orgs_qs = Organization.objects.all()
#     users_qs = User.objects.all()
#     leads_qs = Lead.objects.all()
#     quotations_qs = Quotation.objects.all()
#     subs_qs = OrganizationSubscription.objects.all()
#
#     if selected_org:
#         # Filter to selected organization
#         orgs_qs = orgs_qs.filter(id=selected_org.id)
#         users_qs = users_qs.filter(core_profile__organization=selected_org)
#         leads_qs = leads_qs.filter(organization=selected_org)
#         quotations_qs = quotations_qs.filter(organization=selected_org)
#         subs_qs = subs_qs.filter(organization=selected_org)
#
#     # KPIs
#     total_orgs = orgs_qs.count()
#     active_orgs = orgs_qs.filter(is_active=True).count()
#     suspended_orgs = orgs_qs.filter(is_active=False).count()
#     total_users = users_qs.count()
#     total_leads = leads_qs.count()
#     total_quotations = quotations_qs.count()
#
#     # Revenue (sum of active subscription plan monthly prices)
#     total_revenue = subs_qs.filter(
#         status='active'
#     ).aggregate(total=Sum('plan__monthly_price'))['total'] or 0
#
#     # Subscriptions expiring soon (next 7 days)
#     expiring_soon = OrganizationSubscription.objects.filter(
#         end_date__lte=timezone.now().date() + timedelta(days=7),
#         status='active'
#     ).select_related('organization', 'plan')
#     if selected_org:
#         expiring_soon = expiring_soon.filter(organization=selected_org)
#
#     # All organizations for the dropdown
#     all_orgs = Organization.objects.all().order_by('legal_name')
#
#     # Recent organizations (platform-wide or filtered) – we'll use this for the table
#     recent_orgs = orgs_qs.order_by('-created_at')[:10]  # show up to 10
#
#     context = {
#         'selected_org': selected_org,
#         'total_orgs': total_orgs,
#         'active_orgs': active_orgs,
#         'suspended_orgs': suspended_orgs,
#         'total_users': total_users,
#         'total_leads': total_leads,
#         'total_quotations': total_quotations,
#         'total_revenue': total_revenue,
#         'expiring_soon': expiring_soon,
#         'organizations': all_orgs,
#         'recent_orgs': recent_orgs,
#     }
#     return render(request, 'control_panel/dashboard.html', context)

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from .services import dashboard_service
from apps.core.models import Organization, User
from apps.leads.models import Lead

@permission_required('core.view_platform_dashboard')
def dashboard(request):
    # Get selected organization from session (if any)
    selected_org_id = request.session.get('selected_org_id')
    selected_org = None
    if selected_org_id:
        try:
            selected_org = Organization.objects.get(id=selected_org_id)
        except Organization.DoesNotExist:
            selected_org_id = None
            request.session.pop('selected_org_id', None)

    # Base querysets
    orgs_qs = Organization.objects.all()
    users_qs = User.objects.all()
    leads_qs = Lead.objects.all()
    subs_qs = dashboard_service.get_expiring_subscriptions()  # full platform

    if selected_org:
        # Filter everything to selected organization
        orgs_qs = orgs_qs.filter(id=selected_org.id)
        users_qs = users_qs.filter(core_profile__organization=selected_org)
        leads_qs = leads_qs.filter(organization=selected_org)
        # For subscriptions, we still want expiring for that org only
        subs_qs = subs_qs.filter(organization=selected_org)

    # KPIs
    total_orgs = orgs_qs.count()
    active_orgs = orgs_qs.filter(is_active=True).count()
    suspended_orgs = orgs_qs.filter(is_active=False).count()
    total_users = users_qs.count()
    total_leads = leads_qs.count()

    # Expired subscriptions (platform-wide or filtered)
    expired_subs = dashboard_service.get_expired_subscriptions()
    if selected_org:
        expired_subs = expired_subs.filter(organization=selected_org)

    # Lead stats (only needed when viewing all orgs? We can compute anyway)
    lead_stats = dashboard_service.get_platform_lead_stats()

    # All organizations for dropdown
    all_orgs = Organization.objects.all().order_by('legal_name')

    # Recent organizations (platform-wide or filtered)
    recent_orgs = orgs_qs.order_by('-created_at')[:10]

    context = {
        'selected_org': selected_org,
        'total_orgs': total_orgs,
        'active_orgs': active_orgs,
        'suspended_orgs': suspended_orgs,
        'total_users': total_users,
        'total_leads': total_leads,
        'expiring_subs': subs_qs,           # TASK 1
        'expired_subs': expired_subs,        # TASK 2
        'lead_stats': lead_stats,            # TASK 5
        'organizations': all_orgs,
        'recent_orgs': recent_orgs,
    }
    return render(request, 'control_panel/dashboard.html', context)

# apps/control_panel/views.py (add this)
from django.db.models import Count, Sum
from django.utils import timezone
from apps.core.models import UserProfile
from apps.leads.models import Lead, Campaign   # if Campaign exists
from apps.control_panel.models import OrganizationFeature, AuditLog

@permission_required('core.manage_organizations')
def organization_detail(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    # Gather data
    total_users = UserProfile.objects.filter(organization=org).count()
    total_leads = Lead.objects.filter(organization=org).count()
    total_campaigns = Campaign.objects.filter(organization=org).count() if hasattr(Campaign, 'organization') else 0
    # Subscription
    subscription = OrganizationSubscription.objects.filter(organization=org).select_related('plan').first()
    # Feature flags
    features = OrganizationFeature.objects.filter(organization=org).select_related('feature')
    # Recent activity logs (assuming AuditLog model)
    recent_activity = AuditLog.objects.filter(
        content_type__app_label='core',
        object_id=org.id
    ).order_by('-timestamp')[:10]
    # Last login activity – we need to get last login of users in this org
    last_login = UserProfile.objects.filter(organization=org).select_related('user').order_by('-user__last_login').first()
    last_login_activity = last_login.user.last_login if last_login else None

    context = {
        'org': org,
        'total_users': total_users,
        'total_leads': total_leads,
        'total_campaigns': total_campaigns,
        'subscription': subscription,
        'features': features,
        'recent_activity': recent_activity,
        'last_login_activity': last_login_activity,
        # storage usage if tracked
    }
    return render(request, 'control_panel/organization_detail.html', context)

# ---------- Organizations ----------
class OrganizationListView(SuperuserRequiredMixin, ListView):
    model = Organization
    template_name = 'control_panel/organizations_list.html'
    context_object_name = 'organizations'
    ordering = ['-created_at']

class OrganizationCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'control_panel/organization_form.html'
    success_url = reverse_lazy('control_panel:organizations')
    success_message = "Organization '%(legal_name)s' created successfully."

class OrganizationUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'control_panel/organization_form.html'
    success_url = reverse_lazy('control_panel:organizations')
    success_message = "Organization '%(legal_name)s' updated successfully."

class OrganizationDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Organization
    template_name = 'control_panel/organization_confirm_delete.html'
    success_url = reverse_lazy('control_panel:organizations')
    success_message = "Organization deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)




@permission_required('core.manage_organizations')
def organization_limits(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    if request.method == 'POST':
        form = OrganizationLimitsForm(request.POST, instance=org)
        if form.is_valid():
            form.save()
            return redirect('control_panel:dashboard')
    else:
        form = OrganizationLimitsForm(instance=org)
    return render(request, 'control_panel/org_limits_form.html', {'form': form, 'org': org})


# ---------- Users ----------
class UserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'control_panel/users_list.html'
    context_object_name = 'users'
    ordering = ['-date_joined']

class UserCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'control_panel/user_form.html'
    success_url = reverse_lazy('control_panel:users')
    success_message = "User '%(username)s' created successfully. You must set a password separately."

    def form_valid(self, form):
        response = super().form_valid(form)
        # After user is saved, create a profile if needed? The profile may be created by signal or manually.
        # We'll also handle profile separately.
        return response

class UserUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'control_panel/user_form.html'
    success_url = reverse_lazy('control_panel:users')
    success_message = "User '%(username)s' updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, 'core_profile'):
            context['profile_form'] = UserProfileForm(instance=self.object.core_profile)
        else:
            context['profile_form'] = UserProfileForm(initial={'user': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        profile_form = UserProfileForm(request.POST, instance=getattr(self.object, 'core_profile', None))
        if form.is_valid() and profile_form.is_valid():
            response = self.form_valid(form)
            profile = profile_form.save(commit=False)
            profile.user = self.object
            profile.save()
            return response
        else:
            return self.form_invalid(form)

class UserDeleteView(SuperuserRequiredMixin, DeleteView):
    model = User
    template_name = 'control_panel/user_confirm_delete.html'
    success_url = reverse_lazy('control_panel:users')
    success_message = "User deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# ---------- Roles ----------
class RoleListView(SuperuserRequiredMixin, ListView):
    model = Role
    template_name = 'control_panel/roles_list.html'
    context_object_name = 'roles'
    ordering = ['name']



def get_role_permissions(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    role = get_object_or_404(Role, pk=pk)
    assigned = set(role.permissions.values_list('id', flat=True))
    permissions = Permission.objects.all().order_by('app_label', 'codename')
    data = {
        'role_name': role.name,
        'permissions': []
    }
    for perm in permissions:
        data['permissions'].append({
            'id': perm.id,
            'app_label': perm.app_label,
            'codename': perm.codename,
            'name': perm.name,
            'assigned': perm.id in assigned,
        })
    return JsonResponse(data)

from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
@require_POST
def update_role_permissions(request, pk):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    role = get_object_or_404(Role, pk=pk)
    permission_ids = request.POST.getlist('permissions')
    role.permissions.set(permission_ids)
    return JsonResponse({'success': True})

class RoleCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'control_panel/role_form.html'
    success_url = reverse_lazy('control_panel:roles')
    success_message = "Role '%(name)s' created successfully."

class RoleUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'control_panel/role_form.html'
    success_url = reverse_lazy('control_panel:roles')
    success_message = "Role '%(name)s' updated successfully."

class RoleDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Role
    template_name = 'control_panel/role_confirm_delete.html'
    success_url = reverse_lazy('control_panel:roles')
    success_message = "Role deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# ---------- Subscriptions ----------
class SubscriptionPlanListView(SuperuserRequiredMixin, ListView):
    model = SubscriptionPlan
    template_name = 'control_panel/subscriptions_list.html'
    context_object_name = 'plans'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriptions'] = OrganizationSubscription.objects.all().select_related('organization', 'plan')
        return context

class SubscriptionPlanCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm
    template_name = 'control_panel/subscriptionplan_form.html'
    success_url = reverse_lazy('control_panel:subscriptions')
    success_message = "Plan '%(name)s' created successfully."

class SubscriptionPlanUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm
    template_name = 'control_panel/subscriptionplan_form.html'
    success_url = reverse_lazy('control_panel:subscriptions')
    success_message = "Plan '%(name)s' updated successfully."

class SubscriptionPlanDeleteView(SuperuserRequiredMixin, DeleteView):
    model = SubscriptionPlan
    template_name = 'control_panel/subscription_confirm_delete.html'
    success_url = reverse_lazy('control_panel:subscriptions')
    success_message = "Plan deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class OrganizationSubscriptionCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = OrganizationSubscription
    form_class = OrganizationSubscriptionForm
    template_name = 'control_panel/organizationsubscription_form.html'
    success_url = reverse_lazy('control_panel:subscriptions')
    success_message = "Subscription assigned successfully."

class OrganizationSubscriptionUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OrganizationSubscription
    form_class = OrganizationSubscriptionForm
    template_name = 'control_panel/organizationsubscription_form.html'
    success_url = reverse_lazy('control_panel:subscriptions')
    success_message = "Subscription updated successfully."

class OrganizationSubscriptionDeleteView(SuperuserRequiredMixin, DeleteView):
    model = OrganizationSubscription
    template_name = 'control_panel/subscription_confirm_delete.html'
    success_url = reverse_lazy('control_panel:subscriptions')
    success_message = "Subscription deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# ---------- Feature Flags ----------
class FeatureListView(SuperuserRequiredMixin, ListView):
    model = Feature
    template_name = 'control_panel/feature_flags_list.html'
    context_object_name = 'features'
    ordering = ['codename']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['org_features'] = OrganizationFeature.objects.all().select_related('organization', 'feature')
        return context

class FeatureCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'control_panel/feature_form.html'
    success_url = reverse_lazy('control_panel:feature_flags')
    success_message = "Feature '%(codename)s' created successfully."

class FeatureUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'control_panel/feature_form.html'
    success_url = reverse_lazy('control_panel:feature_flags')
    success_message = "Feature '%(codename)s' updated successfully."

class FeatureDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Feature
    template_name = 'control_panel/feature_confirm_delete.html'
    success_url = reverse_lazy('control_panel:feature_flags')
    success_message = "Feature deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class OrganizationFeatureCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    model = OrganizationFeature
    form_class = OrganizationFeatureForm
    template_name = 'control_panel/organizationfeature_form.html'
    success_url = reverse_lazy('control_panel:feature_flags')
    success_message = "Organization feature override created."

class OrganizationFeatureUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = OrganizationFeature
    form_class = OrganizationFeatureForm
    template_name = 'control_panel/organizationfeature_form.html'
    success_url = reverse_lazy('control_panel:feature_flags')
    success_message = "Organization feature override updated."

class OrganizationFeatureDeleteView(SuperuserRequiredMixin, DeleteView):
    model = OrganizationFeature
    template_name = 'control_panel/feature_confirm_delete.html'
    success_url = reverse_lazy('control_panel:feature_flags')
    success_message = "Organization feature override deleted."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)



class AuditLogListView(SuperuserRequiredMixin, ListView):
    model = AuditLog
    template_name = 'control_panel/audit_logs_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    ordering = ['-timestamp']
