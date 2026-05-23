from django.contrib import admin
from .models import SalesTarget, SalesAchievement

@admin.register(SalesTarget)
class SalesTargetAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'lead_target', 'revenue_target']

@admin.register(SalesAchievement)
class SalesAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'leads_acquired', 'revenue_generated']