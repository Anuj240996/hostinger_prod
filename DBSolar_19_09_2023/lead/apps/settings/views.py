# # from django.shortcuts import render, redirect, get_object_or_404
# # from django.contrib.admin.views.decorators import staff_member_required
# # from django.contrib import messages
# # from django.http import JsonResponse
# #
# # from apps.leads.models import LeadSource, Campaign
# # from .models import SystemSetting, LostReason, ScoringRule
# #
# #
# # @staff_member_required
# # def settings_dashboard(request):
# #     """
# #     Settings dashboard with all configuration tabs
# #     """
# #     context = {
# #         'lead_sources': LeadSource.objects.all(),
# #         'campaigns': Campaign.objects.all().select_related('source'),
# #         'lost_reasons': LostReason.objects.filter(is_active=True),
# #         'scoring_rules': ScoringRule.objects.filter(is_active=True),
# #     }
# #
# #     return render(request, 'settings/settings.html', context)
# #
# #
# # # Lead Sources CRUD
# # @staff_member_required
# # def add_lead_source(request):
# #     if request.method == 'POST':
# #         name = request.POST.get('name')
# #         cost = request.POST.get('cost_per_lead')
# #
# #         source = LeadSource.objects.create(
# #             name=name,
# #             cost_per_lead=cost or 0
# #         )
# #
# #         return JsonResponse({'success': True, 'id': source.id})
# #
# #     return JsonResponse({'success': False})
# #
# #
# # @staff_member_required
# # def edit_lead_source(request, pk):
# #     source = get_object_or_404(LeadSource, pk=pk)
# #
# #     if request.method == 'POST':
# #         source.name = request.POST.get('name', source.name)
# #         source.cost_per_lead = request.POST.get('cost_per_lead', source.cost_per_lead)
# #         source.is_active = request.POST.get('is_active') == 'true'
# #         source.save()
# #
# #         return JsonResponse({'success': True})
# #
# #     return JsonResponse({'success': False})
# #
# #
# # @staff_member_required
# # def toggle_lead_source(request, pk):
# #     source = get_object_or_404(LeadSource, pk=pk)
# #     source.is_active = not source.is_active
# #     source.save()
# #
# #     return JsonResponse({'success': True, 'is_active': source.is_active})
# #
# #
# # # Lost Reasons CRUD
# # @staff_member_required
# # def add_lost_reason(request):
# #     if request.method == 'POST':
# #         name = request.POST.get('name')
# #
# #         reason = LostReason.objects.create(name=name)
# #
# #         return JsonResponse({'success': True, 'id': reason.id})
# #
# #     return JsonResponse({'success': False})
# #
# #
# # @staff_member_required
# # def delete_lost_reason(request, pk):
# #     reason = get_object_or_404(LostReason, pk=pk)
# #     reason.delete()
# #
# #     return JsonResponse({'success': True})
# #
# #
# # # Scoring Rules CRUD
# # @staff_member_required
# # def add_scoring_rule(request):
# #     if request.method == 'POST':
# #         rule = ScoringRule.objects.create(
# #             criteria=request.POST.get('criteria'),
# #             condition=request.POST.get('condition'),
# #             value=request.POST.get('value'),
# #             points=request.POST.get('points')
# #         )
# #
# #         return JsonResponse({'success': True, 'id': rule.id})
# #
# #     return JsonResponse({'success': False})
# #
# #
# # @staff_member_required
# # def edit_scoring_rule(request, pk):
# #     rule = get_object_or_404(ScoringRule, pk=pk)
# #
# #     if request.method == 'POST':
# #         rule.criteria = request.POST.get('criteria', rule.criteria)
# #         rule.condition = request.POST.get('condition', rule.condition)
# #         rule.value = request.POST.get('value', rule.value)
# #         rule.points = request.POST.get('points', rule.points)
# #         rule.is_active = request.POST.get('is_active') == 'true'
# #         rule.save()
# #
# #         return JsonResponse({'success': True})
# #
# #     return JsonResponse({'success': False})
# #
# #
# # @staff_member_required
# # def delete_scoring_rule(request, pk):
# #     rule = get_object_or_404(ScoringRule, pk=pk)
# #     rule.delete()
# #
# #     return JsonResponse({'success': True})
# #
# #
# # # System Settings
# # @staff_member_required
# # def update_setting(request):
# #     if request.method == 'POST':
# #         key = request.POST.get('key')
# #         value = request.POST.get('value')
# #
# #         setting, created = SystemSetting.objects.get_or_create(key=key)
# #         setting.value = value
# #         setting.save()
# #
# #         return JsonResponse({'success': True})
# #
# #     return JsonResponse({'success': False})
# #
# #
# #
# #
# # from django.contrib.admin.views.decorators import staff_member_required
# # from django.http import JsonResponse
# # from django.shortcuts import get_object_or_404, render
# # from django.views.decorators.http import require_POST
# #
# # from apps.leads.models import LeadSource, Campaign
# # from apps.pipeline.models import PipelineStage
# # from apps.settings.models import LostReason, ScoringRule
# #
# #
# # @staff_member_required
# # @require_POST
# # def add_pipeline_stage(request):
# #     name = request.POST.get('name')
# #     order = request.POST.get('order')
# #     color = request.POST.get('color')
# #     probability = request.POST.get('probability')
# #     # Get current organization from middleware (request.organization)
# #     org = request.organization
# #     if not org:
# #         return JsonResponse({'success': False, 'errors': 'No organization selected'}, status=400)
# #     stage = PipelineStage.objects.create(
# #         name=name,
# #         order=order,
# #         color=color,
# #         probability=probability,
# #         is_active=True,
# #         organization=org
# #     )
# #     return JsonResponse({
# #         'success': True,
# #         'stage': {
# #             'id': stage.id,
# #             'name': stage.name,
# #             'order': stage.order,
# #             'color': stage.color,
# #             'probability': stage.probability,
# #             'is_active': stage.is_active,
# #         }
# #     })
# #
# # @staff_member_required
# # @require_POST
# # def edit_pipeline_stage(request, pk):
# #     stage = get_object_or_404(PipelineStage, pk=pk)
# #     stage.name = request.POST.get('name', stage.name)
# #     stage.order = request.POST.get('order', stage.order)
# #     stage.color = request.POST.get('color', stage.color)
# #     stage.probability = request.POST.get('probability', stage.probability)
# #     stage.is_active = request.POST.get('is_active') == 'on'
# #     stage.save()
# #     return JsonResponse({'success': True})
# #
# # @staff_member_required
# # @require_POST
# # def delete_pipeline_stage(request, pk):
# #     stage = get_object_or_404(PipelineStage, pk=pk)
# #     stage.delete()
# #     return JsonResponse({'success': True})
# #
# # from apps.pipeline.models import PipelineStage
# #
# # @staff_member_required
# # def settings_dashboard(request):
# #     context = {
# #         'lead_sources': LeadSource.objects.all(),
# #         'campaigns': Campaign.objects.all().select_related('source'),
# #         'lost_reasons': LostReason.objects.filter(is_active=True),
# #         'scoring_rules': ScoringRule.objects.filter(is_active=True),
# #         'pipeline_stages': PipelineStage.objects.all().order_by('order'),
# #     }
# #     return render(request, 'settings/settings.html', context)
# #
# #
# from django.shortcuts import render, get_object_or_404
# from django.contrib.admin.views.decorators import staff_member_required
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
# from django.contrib import messages
# import json
#
# from apps.leads.models import LeadSource, Campaign
# from apps.pipeline.models import PipelineStage
# from .models import LostReason, ScoringRule
# from .forms import LeadSourceForm, CampaignForm, LostReasonForm, ScoringRuleForm
#
# from django.contrib.auth.models import Group, Permission
# from django.contrib.contenttypes.models import ContentType
#
#
# @staff_member_required
# def settings_dashboard(request):
#     # Add roles (groups) to context
#     from django.contrib.auth.models import Group
#     roles = Group.objects.all().order_by('name')
#     # Get all permissions for the permissions panel
#     all_permissions = Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'name')
#
#     """Main settings page."""
#     context = {
#         'lead_sources': LeadSource.objects.filter(organization=request.organization),
#         'campaigns': Campaign.objects.filter(organization=request.organization).select_related('source'),
#         'lost_reasons': LostReason.objects.filter(organization=request.organization, is_active=True),
#         'scoring_rules': ScoringRule.objects.filter(organization=request.organization, is_active=True),
#         'pipeline_stages': PipelineStage.objects.filter(organization=request.organization).order_by('order'),
#         'roles': roles,
#         'all_permissions': all_permissions,
#
#     }
#     return render(request, 'settings/settings.html', context)
#
#
#
# @staff_member_required
# @require_POST
# def add_role(request):
#     name = request.POST.get('name')
#     if not name:
#         return JsonResponse({'success': False, 'errors': 'Role name is required.'}, status=400)
#     group, created = Group.objects.get_or_create(name=name)
#     if created:
#         return JsonResponse({'success': True, 'role': {'id': group.id, 'name': group.name}})
#     else:
#         return JsonResponse({'success': False, 'errors': 'A role with that name already exists.'}, status=400)
#
# @staff_member_required
# @require_POST
# def edit_role(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     name = request.POST.get('name')
#     if not name:
#         return JsonResponse({'success': False, 'errors': 'Role name is required.'}, status=400)
#     if Group.objects.exclude(pk=pk).filter(name=name).exists():
#         return JsonResponse({'success': False, 'errors': 'A role with that name already exists.'}, status=400)
#     group.name = name
#     group.save()
#     return JsonResponse({'success': True})
#
# @staff_member_required
# def get_role_permissions(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     assigned = group.permissions.values_list('id', flat=True)
#     # Return all permissions with an 'assigned' flag
#     perms = []
#     for p in Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'name'):
#         perms.append({
#             'id': p.id,
#             'name': str(p),
#             'content_type': p.content_type.app_label,
#             'assigned': p.id in assigned,
#         })
#     return JsonResponse({'permissions': perms})
#
# @staff_member_required
# @require_POST
# def update_role_permissions(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     permission_ids = request.POST.getlist('permissions')
#     # Clear existing and set new ones
#     group.permissions.set(permission_ids)
#     return JsonResponse({'success': True})
#
# # -------------------- Pipeline Stages --------------------
# @staff_member_required
# @require_POST
# def add_pipeline_stage(request):
#     name = request.POST.get('name')
#     order = request.POST.get('order')
#     color = request.POST.get('color')
#     probability = request.POST.get('probability')
#     org = request.organization
#     if not org:
#         return JsonResponse({'success': False, 'errors': 'No organization selected'}, status=400)
#     stage = PipelineStage.objects.create(
#         name=name,
#         order=order,
#         color=color,
#         probability=probability,
#         is_active=True,
#         organization=org
#     )
#     return JsonResponse({
#         'success': True,
#         'stage': {
#             'id': stage.id,
#             'name': stage.name,
#             'order': stage.order,
#             'color': stage.color,
#             'probability': stage.probability,
#         }
#     })
#
#
# @staff_member_required
# def get_pipeline_stage(request, pk):
#     stage = get_object_or_404(PipelineStage, pk=pk, organization=request.organization)
#     return JsonResponse({
#         'id': stage.id,
#         'name': stage.name,
#         'order': stage.order,
#         'color': stage.color,
#         'probability': stage.probability,
#         'is_active': stage.is_active,
#     })
#
#
# @staff_member_required
# @require_POST
# def edit_pipeline_stage(request, pk):
#     stage = get_object_or_404(PipelineStage, pk=pk, organization=request.organization)
#     stage.name = request.POST.get('name', stage.name)
#     stage.order = request.POST.get('order', stage.order)
#     stage.color = request.POST.get('color', stage.color)
#     stage.probability = request.POST.get('probability', stage.probability)
#     stage.is_active = request.POST.get('is_active') == 'on'
#     stage.save()
#     return JsonResponse({'success': True})
#
#
# @staff_member_required
# @require_POST
# def delete_pipeline_stage(request, pk):
#     stage = get_object_or_404(PipelineStage, pk=pk, organization=request.organization)
#     stage.delete()
#     return JsonResponse({'success': True})
#
#
# # -------------------- Lead Sources --------------------
# @staff_member_required
# @require_POST
# def add_lead_source(request):
#     form = LeadSourceForm(request.POST)
#     if form.is_valid():
#         source = form.save(commit=False)
#         source.organization = request.organization
#         source.save()
#         return JsonResponse({
#             'success': True,
#             'source': {
#                 'id': source.id,
#                 'name': source.name,
#                 'cost_per_lead': str(source.cost_per_lead),
#                 'is_active': source.is_active,
#             }
#         })
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
#
# @staff_member_required
# @require_POST
# def edit_lead_source(request, pk):
#     source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
#     form = LeadSourceForm(request.POST, instance=source)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
# #
# # @staff_member_required
# # @require_POST
# # def toggle_lead_source(request, pk):
# #     source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
# #     source.is_active = not source.is_active
# #     source.save()
# #     return JsonResponse({'success': True, 'is_active': source.is_active})
#
# @staff_member_required
# @require_POST
# def delete_lead_source(request, pk):
#     source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
#     source.delete()
#     return JsonResponse({'success': True})
#
# @staff_member_required
# def get_lead_source(request, pk):
#     source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
#     return JsonResponse({
#         'id': source.id,
#         'name': source.name,
#         'cost_per_lead': str(source.cost_per_lead),
#         'is_active': source.is_active,
#     })
#
# # -------------------- Campaigns --------------------
# @staff_member_required
# @require_POST
# def add_campaign(request):
#     form = CampaignForm(request.POST)
#     if form.is_valid():
#         campaign = form.save(commit=False)
#         campaign.organization = request.organization
#         campaign.save()
#         return JsonResponse({
#             'success': True,
#             'campaign': {
#                 'id': campaign.id,
#                 'name': campaign.name,
#                 'source': campaign.source.name,
#                 'start_date': campaign.start_date.strftime('%Y-%m-%d'),
#                 'end_date': campaign.end_date.strftime('%Y-%m-%d'),
#                 'budget': str(campaign.budget),
#                 'is_active': campaign.is_active,
#             }
#         })
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
#
# @staff_member_required
# @require_POST
# def edit_campaign(request, pk):
#     campaign = get_object_or_404(Campaign, pk=pk, organization=request.organization)
#     form = CampaignForm(request.POST, instance=campaign)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
#
# # -------------------- Lost Reasons --------------------
# @staff_member_required
# @require_POST
# def add_lost_reason(request):
#     form = LostReasonForm(request.POST)
#     if form.is_valid():
#         reason = form.save(commit=False)
#         reason.organization = request.organization
#         reason.save()
#         return JsonResponse({'success': True, 'reason': {'id': reason.id, 'name': reason.name}})
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
#
# @staff_member_required
# @require_POST
# def delete_lost_reason(request, pk):
#     reason = get_object_or_404(LostReason, pk=pk, organization=request.organization)
#     reason.delete()
#     return JsonResponse({'success': True})
#
#
# # -------------------- Scoring Rules --------------------
# @staff_member_required
# @require_POST
# def add_scoring_rule(request):
#     form = ScoringRuleForm(request.POST)
#     if form.is_valid():
#         rule = form.save(commit=False)
#         rule.organization = request.organization
#         rule.save()
#         return JsonResponse({
#             'success': True,
#             'rule': {
#                 'id': rule.id,
#                 'criteria': rule.get_criteria_display(),
#                 'condition': rule.get_condition_display(),
#                 'value': rule.value,
#                 'points': rule.points,
#                 'is_active': rule.is_active,
#             }
#         })
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
#
# @staff_member_required
# @require_POST
# def edit_scoring_rule(request, pk):
#     rule = get_object_or_404(ScoringRule, pk=pk, organization=request.organization)
#     form = ScoringRuleForm(request.POST, instance=rule)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
#
#
# @staff_member_required
# @require_POST
# def delete_scoring_rule(request, pk):
#     rule = get_object_or_404(ScoringRule, pk=pk, organization=request.organization)
#     rule.delete()
#     return JsonResponse({'success': True})

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.models import Group, Permission

from apps.leads.models import LeadSource, Campaign
from apps.pipeline.models import PipelineStage
from apps.core.models import Organization, UserProfile
from apps.core.utils import generate_unique_subdomain
from apps.core.utils import add_default_data_for_organization
from .models import LostReason, ScoringRule
from .forms import LeadSourceForm, CampaignForm, LostReasonForm, ScoringRuleForm


from functools import wraps
from django.http import HttpResponseForbidden

def _resolve_organization(request):
    """Resolve organization for settings actions with safe fallbacks."""
    org = getattr(request, 'organization', None)
    if org:
        return org

    if hasattr(request.user, 'core_profile') and request.user.core_profile.organization:
        org = request.user.core_profile.organization
    elif request.user.is_superuser:
        org = Organization.objects.order_by('id').first()

    # Bootstrap a default org/profile for migrated existing-project users.
    if not org and request.user.is_authenticated:
        email = (request.user.email or '').strip().lower() or f"{request.user.username}@local.invalid"
        legal_name = "Default Organization"
        subdomain = generate_unique_subdomain(legal_name)
        org = Organization.objects.create(
            legal_name=legal_name,
            business_type='other',
            address_line1='Default Address',
            city='Default City',
            state='Default State',
            country='India',
            postal_code='000000',
            official_email=f"{request.user.username}.{request.user.id}@local.invalid" if Organization.objects.filter(official_email=email).exists() else email,
            phone='0000000000',
            subdomain=subdomain,
        )
        add_default_data_for_organization(org)

    if org and request.user.is_authenticated and not hasattr(request.user, 'core_profile'):
        UserProfile.objects.create(
            user=request.user,
            organization=org,
            phone='',
            is_tenant_admin=True,
        )

    request.organization = org
    return org

def settings_permission_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.is_superuser or
            (hasattr(request.user, 'core_profile') and request.user.core_profile.is_tenant_admin)
        ):
            _resolve_organization(request)
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page.")
    return wrapped


# @staff_member_required
@settings_permission_required
def settings_dashboard(request):
    """Main settings page."""
    # roles = Group.objects.all().order_by('name')
    roles = Role.objects.filter(organization=request.organization).order_by('name')
    context = {
        'lead_sources': LeadSource.objects.filter(organization=request.organization),
        'campaigns': Campaign.objects.filter(organization=request.organization).select_related('source'),
        'lost_reasons': LostReason.objects.filter(organization=request.organization, is_active=True),
        'scoring_rules': ScoringRule.objects.filter(organization=request.organization, is_active=True),
        'pipeline_stages': PipelineStage.objects.filter(organization=request.organization).order_by('order'),
        'roles': roles,
    }
    return render(request, 'settings/settings.html', context)


# -------------------- Pipeline Stages --------------------
# @staff_member_required
@settings_permission_required
@require_POST
def add_pipeline_stage(request):
    name = request.POST.get('name')
    order = request.POST.get('order')
    color = request.POST.get('color')
    probability = request.POST.get('probability')
    org = request.organization
    if not org:
        return JsonResponse({'success': False, 'errors': 'No organization selected'}, status=400)
    stage = PipelineStage.objects.create(
        name=name,
        order=order,
        color=color,
        probability=probability,
        is_active=True,
        organization=org
    )
    return JsonResponse({
        'success': True,
        'stage': {
            'id': stage.id,
            'name': stage.name,
            'order': stage.order,
            'color': stage.color,
            'probability': stage.probability,
        }
    })


# @staff_member_required
@settings_permission_required
def get_pipeline_stage(request, pk):
    stage = get_object_or_404(PipelineStage, pk=pk, organization=request.organization)
    return JsonResponse({
        'id': stage.id,
        'name': stage.name,
        'order': stage.order,
        'color': stage.color,
        'probability': stage.probability,
        'is_active': stage.is_active,
    })


# @staff_member_required
@settings_permission_required
@require_POST
def edit_pipeline_stage(request, pk):
    stage = get_object_or_404(PipelineStage, pk=pk, organization=request.organization)
    stage.name = request.POST.get('name', stage.name)
    stage.order = request.POST.get('order', stage.order)
    stage.color = request.POST.get('color', stage.color)
    stage.probability = request.POST.get('probability', stage.probability)
    stage.is_active = request.POST.get('is_active') == 'on'
    stage.save()
    return JsonResponse({'success': True})


# @staff_member_required
@settings_permission_required
@require_POST
def delete_pipeline_stage(request, pk):
    stage = get_object_or_404(PipelineStage, pk=pk, organization=request.organization)
    stage.delete()
    return JsonResponse({'success': True})


# -------------------- Lead Sources --------------------


# @staff_member_required
@settings_permission_required
@require_POST
def add_lead_source(request):
    form = LeadSourceForm(request.POST)
    if form.is_valid():
        source = form.save(commit=False)
        source.organization = request.organization
        source.save()
        return JsonResponse({
            'success': True,
            'source': {
                'id': source.id,
                'name': source.name,
                'cost_per_lead': str(source.cost_per_lead),
                'is_active': source.is_active,
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# @staff_member_required
@settings_permission_required
@require_POST
def edit_lead_source(request, pk):
    source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
    form = LeadSourceForm(request.POST, instance=source)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

# @staff_member_required
@settings_permission_required
def get_lead_source(request, pk):
    source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
    return JsonResponse({
        'id': source.id,
        'name': source.name,
        'cost_per_lead': str(source.cost_per_lead),
        'is_active': source.is_active,
    })
#
# @staff_member_required
@settings_permission_required
@require_POST
def toggle_lead_source(request, pk):
    source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
    source.is_active = not source.is_active
    source.save()
    return JsonResponse({'success': True, 'is_active': source.is_active})


# @staff_member_required
@settings_permission_required
@require_POST
def delete_lead_source(request, pk):
    source = get_object_or_404(LeadSource, pk=pk, organization=request.organization)
    source.delete()
    return JsonResponse({'success': True})


# -------------------- Campaigns --------------------
# @staff_member_required
@settings_permission_required
@require_POST
def add_campaign(request):
    form = CampaignForm(request.POST, organization=request.organization)
    if form.is_valid():
        campaign = form.save(commit=False)
        campaign.organization = request.organization
        campaign.save()
        return JsonResponse({
            'success': True,
            'campaign': {
                'id': campaign.id,
                'name': campaign.name,
                'source': campaign.source.name,
                'start_date': campaign.start_date.strftime('%Y-%m-%d'),
                'end_date': campaign.end_date.strftime('%Y-%m-%d'),
                'budget': str(campaign.budget),
                'is_active': campaign.is_active,
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# @staff_member_required
@settings_permission_required
@require_POST
def edit_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, organization=request.organization)
    form = CampaignForm(request.POST, instance=campaign, organization=request.organization)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

# @staff_member_required
@settings_permission_required
def get_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk, organization=request.organization)
    return JsonResponse({
        'id': campaign.id,
        'name': campaign.name,
        'source': campaign.source.id,          # send the ID for pre-selecting the dropdown
        'start_date': campaign.start_date.strftime('%Y-%m-%d'),
        'end_date': campaign.end_date.strftime('%Y-%m-%d'),
        'budget': str(campaign.budget),
        'is_active': campaign.is_active,
    })

# -------------------- Lost Reasons --------------------
# @staff_member_required
# @require_POST
# def add_lost_reason(request):
#     form = LostReasonForm(request.POST)
#     if form.is_valid():
#         reason = form.save(commit=False)
#         reason.organization = request.organization
#         reason.save()
#         return JsonResponse({'success': True, 'reason': {'id': reason.id, 'name': reason.name}})
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
# @staff_member_required
@settings_permission_required
@require_POST
def add_lost_reason(request):
    form = LostReasonForm(request.POST, organization=request.organization)
    if form.is_valid():
        reason = form.save(commit=False)
        reason.organization = request.organization
        reason.save()
        return JsonResponse({'success': True, 'reason': {'id': reason.id, 'name': reason.name}})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

# @staff_member_required
@settings_permission_required
@require_POST
def edit_lost_reason(request, pk):
    reason = get_object_or_404(LostReason, pk=pk, organization=request.organization)
    form = LostReasonForm(request.POST, instance=reason, organization=request.organization)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# @staff_member_required
@settings_permission_required
@require_POST
def delete_lost_reason(request, pk):
    reason = get_object_or_404(LostReason, pk=pk, organization=request.organization)
    reason.delete()
    return JsonResponse({'success': True})


# -------------------- Scoring Rules --------------------
# @staff_member_required
# @require_POST
# def add_scoring_rule(request):
#     form = ScoringRuleForm(request.POST)
#     if form.is_valid():
#         rule = form.save(commit=False)
#         rule.organization = request.organization
#         rule.save()
#         return JsonResponse({
#             'success': True,
#             'rule': {
#                 'id': rule.id,
#                 'criteria': rule.get_criteria_display(),
#                 'condition': rule.get_condition_display(),
#                 'value': rule.value,
#                 'points': rule.points,
#                 'is_active': rule.is_active,
#             }
#         })
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)

# @staff_member_required
@settings_permission_required
@require_POST
def add_scoring_rule(request):
    form = ScoringRuleForm(request.POST)
    if form.is_valid():
        rule = form.save(commit=False)
        rule.organization = request.organization
        rule.save()
        return JsonResponse({
            'success': True,
            'rule': {
                'id': rule.id,
                'criteria': rule.get_criteria_display(),
                'condition': rule.get_condition_display(),
                'value': rule.value,
                'points': rule.points,
                'is_active': rule.is_active,
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

# @staff_member_required
@settings_permission_required
@require_POST
def edit_scoring_rule(request, pk):
    rule = get_object_or_404(ScoringRule, pk=pk, organization=request.organization)
    form = ScoringRuleForm(request.POST, instance=rule)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)

# @staff_member_required
@settings_permission_required
def get_scoring_rule(request, pk):
    rule = get_object_or_404(ScoringRule, pk=pk, organization=request.organization)
    return JsonResponse({
        'id': rule.id,
        'criteria': rule.criteria,
        'condition': rule.condition,
        'value': rule.value,
        'points': rule.points,
        'is_active': rule.is_active,
    })

# @staff_member_required
@settings_permission_required
@require_POST
def delete_scoring_rule(request, pk):
    rule = get_object_or_404(ScoringRule, pk=pk, organization=request.organization)
    rule.delete()
    return JsonResponse({'success': True})


# -------------------- User Roles (Groups) --------------------
# @staff_member_required
# @require_POST
# def add_role(request):
#     name = request.POST.get('name')
#     if not name:
#         return JsonResponse({'success': False, 'errors': 'Role name is required.'}, status=400)
#     group, created = Group.objects.get_or_create(name=name)
#     if created:
#         return JsonResponse({'success': True, 'role': {'id': group.id, 'name': group.name}})
#     else:
#         return JsonResponse({'success': False, 'errors': 'A role with that name already exists.'}, status=400)
#
#
# @staff_member_required
# @require_POST
# def edit_role(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     name = request.POST.get('name')
#     if not name:
#         return JsonResponse({'success': False, 'errors': 'Role name is required.'}, status=400)
#     if Group.objects.exclude(pk=pk).filter(name=name).exists():
#         return JsonResponse({'success': False, 'errors': 'A role with that name already exists.'}, status=400)
#     group.name = name
#     group.save()
#     return JsonResponse({'success': True})
#
# #
# # @staff_member_required
# # def get_role_permissions(request, pk):
# #     group = get_object_or_404(Group, pk=pk)
# #     assigned = group.permissions.values_list('id', flat=True)
# #     perms = []
# #     for p in Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'name'):
# #         perms.append({
# #             'id': p.id,
# #             'name': str(p),
# #             'content_type': p.content_type.app_label,
# #             'assigned': p.id in assigned,
# #         })
# #     return JsonResponse({'permissions': perms})
#
# @staff_member_required
# def get_role_permissions(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     assigned = group.permissions.values_list('id', flat=True)
#     perms = []
#     for p in Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'name'):
#         perms.append({
#             'id': p.id,
#             'name': str(p),
#             'codename': p.codename,
#             'content_type': p.content_type.app_label,
#             'assigned': p.id in assigned,
#         })
#     return JsonResponse({'permissions': perms})
#
# @staff_member_required
# @require_POST
# def update_role_permissions(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     permission_ids = request.POST.getlist('permissions')
#     group.permissions.set(permission_ids)
#     return JsonResponse({'success': True})

from apps.control_panel.models import Role, RolePermission
from django.contrib.auth.models import Permission

# @staff_member_required
@settings_permission_required
@require_POST
def add_role(request):
    name = request.POST.get('name')
    if not name:
        return JsonResponse({'success': False, 'errors': 'Role name is required.'}, status=400)
    # Create role for the current organization
    role, created = Role.objects.get_or_create(
        name=name,
        organization=request.organization
    )
    if created:
        return JsonResponse({'success': True, 'role': {'id': role.id, 'name': role.name}})
    else:
        return JsonResponse({'success': False, 'errors': 'A role with that name already exists in your organization.'}, status=400)

# @staff_member_required
@settings_permission_required
@require_POST
def edit_role(request, pk):
    role = get_object_or_404(Role, pk=pk, organization=request.organization)
    name = request.POST.get('name')
    if not name:
        return JsonResponse({'success': False, 'errors': 'Role name is required.'}, status=400)
    # Check uniqueness within the organization
    if Role.objects.exclude(pk=pk).filter(organization=request.organization, name=name).exists():
        return JsonResponse({'success': False, 'errors': 'A role with that name already exists.'}, status=400)
    role.name = name
    role.save()
    return JsonResponse({'success': True})

# @staff_member_required
# def get_role_permissions(request, pk):
#     role = get_object_or_404(Role, pk=pk, organization=request.organization)
#     assigned = set(role.permissions.values_list('id', flat=True))
#     perms = []
#     for p in Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'name'):
#         perms.append({
#             'id': p.id,
#             'name': str(p),
#             'codename': p.codename,
#             'content_type': p.content_type.app_label,
#             'assigned': p.id in assigned,
#         })
#     return JsonResponse({'permissions': perms})
#
# @staff_member_required
# @require_POST
# def update_role_permissions(request, pk):
#     role = get_object_or_404(Role, pk=pk, organization=request.organization)
#     permission_ids = request.POST.getlist('permissions')
#     # Use the through model to set permissions
#     role.permissions.set(permission_ids)
#     return JsonResponse({'success': True})


from apps.control_panel.models import Role, Permission as ControlPanelPermission

# @staff_member_required
@settings_permission_required
def get_role_permissions(request, pk):
    role = get_object_or_404(Role, pk=pk, organization=request.organization)
    assigned = set(role.permissions.values_list('id', flat=True))
    perms = []
    for p in ControlPanelPermission.objects.all().order_by('app_label', 'codename'):
        perms.append({
            'id': p.id,
            'name': p.name,
            'codename': p.codename,
            'app_label': p.app_label,
            'assigned': p.id in assigned,
        })
    return JsonResponse({'permissions': perms})

# @staff_member_required
@settings_permission_required
@require_POST
def update_role_permissions(request, pk):
    role = get_object_or_404(Role, pk=pk, organization=request.organization)
    permission_ids = request.POST.getlist('permissions')
    role.permissions.set(permission_ids)
    return JsonResponse({'success': True})
