from django.contrib import admin
from .models import LeadSource, Campaign, Lead, LeadActivity, FollowUp

@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'cost_per_lead']
    list_filter = ['is_active']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'source', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'source']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'stage', 'score', 'assigned_to', 'created']
    list_filter = ['stage', 'score', 'source', 'property_type']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created', 'modified']

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ['lead', 'user', 'activity_type', 'created']
    list_filter = ['activity_type']

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['lead', 'user', 'scheduled_date', 'status']
    list_filter = ['status']