from django.contrib.auth.models import User
from django.db import models
from django.apps import apps


from django.core.files.base import ContentFile

from customer.models import Customer


class BarcodeImage(models.Model):
    id = models.AutoField(primary_key=True)
    barcode_data = models.CharField(max_length=255)
    file_saved_at = models.DateTimeField()
    image = models.ImageField(upload_to='static/barcode_images')
    barcode_type = models.CharField(max_length=50)
    company = models.CharField(max_length=255, null=True)
    wattage = models.CharField(max_length=50, null=True)
    barcode_path = models.ImageField(upload_to='static/barcode_images')
    #old_image = models.ImageField(upload_to='static/barcode_images', null=True)  # Add old_image field
    product_name = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=255, null=True)
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='assignto_id')
    #AssignTo = models.IntegerField(default=0)
    AssignBy = models.IntegerField(default=0, db_column='assignby')
    stock = models.ForeignKey('inventory.Stock', on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        app_label = 'detect_barcodes'

class InverterImage(models.Model):
    id = models.AutoField(primary_key=True)
    barcode_data = models.CharField(max_length=255)
    file_saved_at = models.DateTimeField()
    image = models.ImageField(upload_to='static/barcode_images')
    barcode_type = models.CharField(max_length=50)
    company = models.CharField(max_length=255, null=True)
    wattage = models.CharField(max_length=50, null=True)
    barcode_path = models.ImageField(upload_to='static/barcode_images')
    #old_image = models.ImageField(upload_to='static/barcode_images', null=True)  # Add old_image field
    product_name = models.CharField(max_length=100, null=True)
    company_name = models.CharField(max_length=255, null=True)
    AssignTo = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='assignto_id')
    #AssignTo = models.IntegerField(default=0)
    AssignBy = models.IntegerField(default=0, db_column='assignby')

    class Meta:
        app_label = 'detect_barcodes'


