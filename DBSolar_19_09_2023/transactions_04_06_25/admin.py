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
from .models import (
    Supplier,
    Vendor,
    PurchaseBill,
    PurchaseItem,
    PurchaseBillDetails,
    PurchaseSerial,
    SaleBill,
    SaleItem,
    SaleBillDetails,
    ReturnSale,
    ReturnSaleItem,
    ReturnBillDetails
)

admin.site.site_header = 'DBSolar Dashboard'

admin.site.register(Supplier)
admin.site.register(Vendor)
admin.site.register(PurchaseBill)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseBillDetails)
admin.site.register(PurchaseSerial)
admin.site.register(SaleBill)
admin.site.register(SaleItem)
admin.site.register(SaleBillDetails)
admin.site.register(ReturnSale)
admin.site.register(ReturnSaleItem)
admin.site.register(ReturnBillDetails)