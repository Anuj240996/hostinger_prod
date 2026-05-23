from django.contrib import admin
from .models import PipelineStage, PipelineHistory

@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'probability', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(PipelineHistory)
class PipelineHistoryAdmin(admin.ModelAdmin):
    list_display = ['lead', 'from_stage', 'to_stage', 'user', 'created']
    list_filter = ['from_stage', 'to_stage']