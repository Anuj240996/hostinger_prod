from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import BarcodeImage, InverterImage
from django.contrib.auth.models import Group

admin.site.site_header = 'DBSolar Dashboard'


# Register your models here.c
admin.site.register(BarcodeImage)
#admin.site.unregister(Group)
admin.site.register(InverterImage)


