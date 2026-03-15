from django.urls import path
from .views import generate_pdf, barcode_image_view, generate1_pdf, get_images, GeneratePDF
from . import views

urlpatterns = [
    path('', views.detect_barcode, name='detect_barcode'),
   # path('', views.detect_barcode, name='detect_barcodes'),
    path('camera_feed', views.camera_feed, name='camera_feed'),
    path('detect_barcodes/', views.detect_barcode, name='detect_barcodes-detect_barcodes'),
    path('get_customer_details/', views.get_customer_details, name='get_customer_details'),
    path('detect_inverter/', views.detect_inverter, name='detect_barcodes-detect_inverter'),
    path('get_inverter_details/', views.get_inverter_details, name='get_inverter_details'),
    #path('barcodepdf/<int:pk>', views.pdf_barcode_create, name='detect_barcodes-barcodepdf'),
    #path('generate-pdf/', views.generate_pdf, name='generate-pdf'),
    path('detect_barcodes1/', views.upload_barcode, name='detect_barcodes-upload_barcode'),
    path('ajax/handle_upload/', views.ajax_handle_upload, name='detect_barcodes-ajax_handle_upload'),
    path('barcodepdf/', barcode_image_view, name='detect_barcodes-barcodepdf'),
    path('get_images/', get_images, name='detect_barcodes-get_images'),
    #path('generate_pdf/', generate1_pdf, name='detect_barcodes-generate_pdf'),
    path('search/', views.search_view, name='detect_barcodes-search'),
    path('generate_pdf/', views.GeneratePDF, name='detect_barcodes-generate_pdf'),
    path('edit_barcode/', views.editbarcode, name='detect_barcodes-edit_barcode'),
    path('display_product/', views.displayproduct, name='detect_barcodes-display_product'),
    path('display_warranty/', views.displaywarranty, name='detect_barcodes-display_warranty'),
    path('editbarcode/', views.editbarcode, name='editbarcode'),  # The URL pattern for your editbarcode view
    path('selected_records/', views.deletebarcode, name='detect_barcodes-selected_records'),  # The URL pattern for your editbarcode view
    # path('scan-barcode/', views.save_barcodes, name='detect_barcodes-scan_barcode'),
    # path('save_barcodes/', views.save_barcodes, name='save_barcodes'),
    path('scan-barcode/', views.realtime_decode, name='detect_barcodes-scan_barcode'),
    path('scan-barcode/', views.scan_barcode, name='scan_barcode'),
    path('serial_barcode/', views.upload_and_display_view, name='detect_barcodes-serial_barcode'),
    path('serial_barcode_inverter/', views.upload_and_display_view_inverter, name='detect_barcodes-serial_barcode_inverter'),
    path('manual_serial_barcode/', views.manual_serial_barcode, name='detect_barcodes-manual_serial_barcode'),
    path('manual_inverter_barcode/', views.manual_serial_barcode, name='detect_barcodes-manual_inverter_barcode'),

    path('search_results/', views.search_barcode, name='detect_barcodes-search_results'),
    # path('serial_barcode/', views.detect_serial_number_and_barcode, name='detect_barcodes-serial_barcode'),

    path('delete_barcode/', views.deletebarcode, name='detect_barcodes-delete_barcode'),
    path('deletebarcode/', views.deletebarcode, name='deletebarcode'),  # The URL pattern for your editbarcode view
    path('promote/', views.promote_view, name='promote_page'),
    path('promote/save_serials/', views.save_selected_serials, name='save_selected_serials'),
]
