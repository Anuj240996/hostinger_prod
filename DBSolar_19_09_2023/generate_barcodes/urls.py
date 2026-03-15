from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate, name='generate_barcodes'),
    path('generate_barcodes/', views.generate, name='generate_barcodes-generate_barcodes'),
    #path('generate_barcodes/', views.barcode_generator, name='generate_barcodes-generate_barcodes'),

]
