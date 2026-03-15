from turtle import home

from django.urls import path
from . import views
# from .views import save_meters, save_generation_meter, save_generation_ct

# urlpatterns = [
#     path('index/', views.index, name='dashboard-index'),
#     path('products/', views.products, name='dashboard-products'),
#     path('products/delete/<int:pk>/', views.product_delete,
#          name='dashboard-products-delete'),
#     path('products/detail/<int:pk>/', views.product_detail,
#          name='dashboard-products-detail'),
#     path('products/edit/<int:pk>/', views.product_edit,
#          name='dashboard-products-edit'),
#     path('customers/', views.customers, name='dashboard-customers'),
#     path('customers/detail/<int:pk>/', views.customer_detail,
#          name='dashboard-customer-detail'),
#     path('order/', views.order, name='dashboard-order'),
# ]

urlpatterns = [
    # path('', views.index, name='customer-index'),
    #path('', views.index, name='index'),
    # path('all_emp', views.all_emp, name='all_emp'),
    # path('add_emp', views.add_emp, name='add_emp'),
    # path('remove_emp', views.remove_emp, name='remove_emp'),
    # path('remove_emp/<int:emp_id>', views.remove_emp, name='remove_emp'),
    # path('filter_emp', views.filter_emp, name='filter_emp'),
    # #path('Cust_emp', views.Cust_emp1, name='Cust_emp'),
    path('index/', views.index, name='customer-index'),
    path('cust/', views.cust, name='customer-cust'),
    path('Cust_emp/', views.Cust_emp, name='customer-Cust_emp'),
    path('Comm_Cust/', views.Comm_Cust, name='customer-Comm_Cust'),
    path('Comp_Cust/', views.Comp_Cust, name='customer-Comp_Cust'),
    path('Govt_Cust/', views.Govt_Cust, name='customer-Govt_Cust'),
    path('Cust_Search/', views.showresults, name='customer-Cust_search'),
    path('view_all_cust/', views.view_all_cust, name='customer-view_all_cust'),
    path('view_all/', views.view_all, name='customer-view_all'),
    path('customer_update/<int:Cust_id>/', views.customer_update, name='customer-customer-update'),
    path('customer_updatepage/<int:Cust_id>/', views.customer_updatepage, name='customer-customer-updatepage'),
    path('Site_Technical_Details/', views.Site_Technical_Details, name='customer-Site_Technical_Details'),
    path('consumer_list/', views.consumer_pdf, name='customer-consumer_list'),
    path('add-meter/', views.add_meter, name='customer-add_meter'),
    path('get_values_for_field/', views.get_values_for_field, name='customer-get_values_for_field'),
    path('search_by_staff', views.search, name='customer-search_by_staff'),

    path('meters', views.newmeters, name='customer-meters'),
    path('save_meters/', views.save_meters, name='save_meters'),
    path('save_generation_meter/', views.save_generation_meter, name='save_generation_meter'),
    path('save_generation_ct/', views.save_generation_ct, name='save_generation_ct'),
    path('edit_meters/', views.edit_records, name='customer-edit_meters'),
    path('display_meters/', views.display_records, name='customer-display_meters'),
    path('change_staff/', views.filter_data, name='customer-change_staff'),
    path('save_change_staff/', views.save_change_staff, name='customer-save_change_staff'),
    # path('fetch-employees/', views.fetch_employees, name='fetch_employees'),


]
