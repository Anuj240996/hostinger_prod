from django.contrib import admin
from .models import Quotation, QuotationItem, QuotationRevision

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1

class QuotationRevisionInline(admin.TabularInline):
    model = QuotationRevision
    extra = 0
    readonly_fields = ['version', 'total_cost', 'created_by', 'created']

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'lead', 'total_cost', 'status', 'created']
    list_filter = ['status']
    inlines = [QuotationItemInline, QuotationRevisionInline]

@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'quotation', 'quantity', 'unit_price', 'total_price']

@admin.register(QuotationRevision)
class QuotationRevisionAdmin(admin.ModelAdmin):
    list_display = ['quotation', 'version', 'total_cost', 'created']