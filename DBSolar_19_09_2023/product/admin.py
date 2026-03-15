from django.contrib import admin
from .models import *
# Register your models here.
#
# admin.site.register(Firereport)
# admin.site.register(Firetequesthistory)
# admin.site.register(Teams)

from django.contrib import admin
from .models import Category, SubCategory, Product, Brand, Unit

admin.site.site_header = 'DBSolar Dashboard'

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Unit)
admin.site.register(Supplier)

