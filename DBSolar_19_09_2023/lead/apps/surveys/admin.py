from django.contrib import admin
from .models import Survey, SurveyImage

class SurveyImageInline(admin.TabularInline):
    model = SurveyImage
    extra = 1

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['lead', 'engineer', 'scheduled_date', 'status', 'feasibility']
    list_filter = ['status', 'feasibility']
    inlines = [SurveyImageInline]

@admin.register(SurveyImage)
class SurveyImageAdmin(admin.ModelAdmin):
    list_display = ['survey', 'caption', 'is_primary']