from django.contrib import admin
from .models import Customer, Employee, Emp_id, customer_technical_Details, Meter, Meters, GenerationMeter, GenerationCT, MSEB, InspectionDetail
from django.contrib.auth.models import Group

admin.site.site_header = 'DBSolar Dashboard'

# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'quantity')
#     list_filter = ['category']
# Register your models here.c
#admin.site.register(Product, ProductAdmin)
#admin.site.unregister(Group)
admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Emp_id)
admin.site.register(customer_technical_Details)
admin.site.register(Meter)
admin.site.register(Meters)
admin.site.register(GenerationMeter)
admin.site.register(GenerationCT)
admin.site.register(MSEB)
admin.site.register(InspectionDetail)



