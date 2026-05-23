# # # from django.contrib import admin
# # # from .models import Organization, Team, Notification
# # #
# # # @admin.register(Organization)
# # # class OrganizationAdmin(admin.ModelAdmin):
# # #     list_display = ['name', 'phone', 'email', 'website']
# # #     search_fields = ['name']
# # #
# # # @admin.register(Team)
# # # class TeamAdmin(admin.ModelAdmin):
# # #     list_display = ['name', 'organization']
# # #     filter_horizontal = ['members']
# # #     search_fields = ['name']
# # #
# # # @admin.register(Notification)
# # # class NotificationAdmin(admin.ModelAdmin):
# # #     list_display = ['user', 'notification_type', 'title', 'is_read', 'created']
# # #     list_filter = ['notification_type', 'is_read']
# # #     search_fields = ['user__username', 'title']
# #
# # from django.contrib import admin
# # from .models import Organization, UserProfile, Team, Notification
# #
# # @admin.register(Organization)
# # class OrganizationAdmin(admin.ModelAdmin):
# #     list_display = ['name', 'subdomain', 'phone', 'email']
# #     search_fields = ['name', 'subdomain']
# #
# # @admin.register(UserProfile)
# # class UserProfileAdmin(admin.ModelAdmin):
# #     list_display = ['user', 'organization', 'phone']
# #     list_filter = ['organization']
# #     search_fields = ['user__username', 'user__email']
# #
# # @admin.register(Team)
# # class TeamAdmin(admin.ModelAdmin):
# #     list_display = ['name', 'organization']
# #     list_filter = ['organization']
# #     filter_horizontal = ['members']
# #     search_fields = ['name']
# #
# # @admin.register(Notification)
# # class NotificationAdmin(admin.ModelAdmin):
# #     list_display = ['user', 'notification_type', 'title', 'is_read', 'created']
# #     list_filter = ['notification_type', 'is_read', 'organization']
# #     search_fields = ['user__username', 'title']
#
#
# from django.contrib import admin
#
# from . import forms
# from .models import Organization, UserProfile, Team, Notification
#
# @admin.register(Organization)
# class OrganizationAdmin(admin.ModelAdmin):
#     list_display = ['legal_name', 'subdomain', 'official_email', 'phone']
#     search_fields = ['legal_name', 'subdomain', 'official_email']
#
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ['user', 'organization', 'phone']
#     list_filter = ['organization']
#     search_fields = ['user__username', 'user__email']
#
# @admin.register(Team)
# class TeamAdmin(admin.ModelAdmin):
#     list_display = ['name', 'organization']
#     list_filter = ['organization']
#     filter_horizontal = ['members']
#     search_fields = ['name']
#
# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ['user', 'notification_type', 'title', 'is_read', 'created']
#     list_filter = ['notification_type', 'is_read', 'organization']
#     search_fields = ['user__username', 'title']
#
from django.contrib import admin
from django import forms
from .models import Organization, UserProfile, Team, Notification

class TenantAwareAdmin(admin.ModelAdmin):
    """Base admin for tenant‑aware models."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by organization from user's profile
        if hasattr(request.user, 'core_profile') and request.user.core_profile.organization:
            return qs.filter(organization=request.user.core_profile.organization)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change and not hasattr(obj, 'organization_id'):
            # Auto‑assign organization on creation for non‑tenant models? Not needed here.
            pass
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and 'organization' in form.base_fields:
            form.base_fields['organization'].disabled = True
            form.base_fields['organization'].widget = forms.HiddenInput()
        return form

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['legal_name', 'subdomain', 'official_email', 'phone', 'is_active']
    search_fields = ['legal_name', 'subdomain', 'official_email']
    list_filter = ['is_active', 'business_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
    # No tenant filtering – superuser only (default)

@admin.register(UserProfile)
class UserProfileAdmin(TenantAwareAdmin):
    list_display = ['user', 'organization', 'phone', 'is_tenant_admin']
    list_filter = ['organization', 'is_tenant_admin']
    search_fields = ['user__username', 'user__email']

@admin.register(Team)
class TeamAdmin(TenantAwareAdmin):
    list_display = ['name', 'organization']
    list_filter = ['organization']
    filter_horizontal = ['members']
    search_fields = ['name']

@admin.register(Notification)
class NotificationAdmin(TenantAwareAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created']
    list_filter = ['notification_type', 'is_read', 'organization']
    search_fields = ['user__username', 'title']
