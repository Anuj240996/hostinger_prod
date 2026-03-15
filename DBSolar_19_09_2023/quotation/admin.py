from django.contrib import admin
from .models import *
# Register your models here.
#
# admin.site.register(Firereport)
# admin.site.register(Firetequesthistory)
# admin.site.register(Teams)

from django.contrib import admin


# from django.contrib import admin
# from .models import Stock
#
# admin.site.site_header = 'DBSolar Dashboard'
#
# admin.site.register(Stock)


from django.contrib import admin

admin.site.site_header = 'DBSolar Dashboard'

# admin.site.register(QuotationCustomer)
# admin.site.register(QuotationProduct)
admin.site.register(Quotation)
# admin.site.register(calculate_totals)
# admin.site.register(QuotationItem)

