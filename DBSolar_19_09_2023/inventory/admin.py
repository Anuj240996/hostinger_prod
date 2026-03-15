from django.contrib import admin
from .models import *
# Register your models here.
#
# admin.site.register(Firereport)
# admin.site.register(Firetequesthistory)
# admin.site.register(Teams)

from django.contrib import admin


from django.contrib import admin
from .models import Stock, FavoriteList

admin.site.site_header = 'DBSolar Dashboard'

admin.site.register(Stock)


