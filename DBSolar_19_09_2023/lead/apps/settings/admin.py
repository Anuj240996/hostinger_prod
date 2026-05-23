from django.contrib import admin
from .models import SystemSetting, LostReason, ScoringRule

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']

@admin.register(LostReason)
class LostReasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']

@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = ['criteria', 'condition', 'value', 'points', 'is_active']
    list_filter = ['criteria', 'is_active']