from turtle import home

from django.urls import path
from . import views
from .views import get_company_data, check_company_name, check_username


urlpatterns = [
    path('index/', views.index, name='customer-index'),
    path('cust/', views.cust, name='customer-cust'),
    path('Cust_emp/', views.Cust_emp, name='customer-Cust_emp'),
    path('Comm_Cust/', views.Comm_Cust, name='customer-Comm_Cust'),
    path('Comp_Cust/', views.Comp_Cust, name='customer-Comp_Cust'),
    path('Govt_Cust/', views.Govt_Cust, name='customer-Govt_Cust'),
    path('check_company_name/', check_company_name, name='check_company_name'),
    path('check-username/', check_username, name='check-username'),
    path('Cust_Search/', views.showresults, name='customer-Cust_search'),
    path('view_all_cust/', views.view_all_cust, name='customer-view_all_cust'),
    path('view_all/', views.view_all, name='customer-view_all'),
    path('customer_update/<int:Cust_id>/', views.customer_update, name='customer-customer-update'),
    path('customer_updatepage/<int:Cust_id>/', views.customer_updatepage, name='customer-customer-updatepage'),
    path('Site_Technical_Details/', views.Site_Technical_Details, name='customer-Site_Technical_Details'),
    path('Site_Inspection_Details/', views.Site_Inspection_Details, name='customer-Site_Inspection_Details'),
    path('get-company-data/', views.get_company_data, name='customer-get_company_data'),
    path('display_Site_Inspection/', views.display_Site_Inspection, name='customer-display_Site_Inspection'),

    path('consumer_list/', views.consumer_pdf, name='customer-consumer_list'),
    path('add-meter/', views.add_meter, name='customer-add_meter'),
    path('get_values_for_field/', views.get_values_for_field, name='customer-get_values_for_field'),
    path('search_by_staff', views.search, name='customer-search_by_staff'),

    path('meters', views.newmeters, name='customer-meters'),
    path('save_meters/', views.save_meters, name='save_meters'),
    path('save_generation_meter/', views.save_generation_meter, name='save_generation_meter'),
    path('filter-comp-names/', views.filter_comp_names, name='filter_comp_names'),
    path('save_generation_ct/', views.save_generation_ct, name='save_generation_ct'),
    path('edit_meters/', views.edit_records, name='customer-edit_meters'),
    path('display_meters/', views.display_records, name='customer-display_meters'),
    path('change_staff/', views.filter_data, name='customer-change_staff'),
    path('save_change_staff/', views.save_change_staff, name='customer-save_change_staff'),
    path('MSEB/', views.mseb_view, name='customer-MSEB'),
    path('complete_MSEB/', views.complete_mseb_view, name='customer-complete_MSEB'),
    path('Update_MSEB/', views.update_mseb_view, name='customer-Update_MSEB'),
    path('get_mseb_data/', views.get_mseb_data, name='customer-get_mseb_data'),
    path('get_customer_data/', views.get_customer_data, name='customer-get_customer_data'),
    path('customer/<int:customer_id>/MSEB_tracking/', views.MSEB_tracking_view, name='customer-MSEB_tracking'),

    path('update_company_name/', views.update_company_name, name='customer-update_company_name'),
    path('search_results/', views.search_barcode, name='customer-search_results'),
    path('solar_pump_new/', views.solar_pump_entry, name='solar_pump_entry'),
    path('update_solar_pump/', views.update_solar_pump, name='update_solar_pump'),


]


