from django.contrib import admin
from .models import Revenue, RevenueTarget

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['lead', 'amount', 'date', 'payment_status']
    list_filter = ['payment_status']

@admin.register(RevenueTarget)
class RevenueTargetAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'target_amount', 'achieved_amount']