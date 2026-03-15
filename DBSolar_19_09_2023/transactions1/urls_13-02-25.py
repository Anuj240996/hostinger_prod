from django.contrib import admin
from django.urls import path
from firereport.views import *
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
#from user import views as user_views




from django.urls import path
# from django.conf.urls import url
from . import views
from .views import supplier_detail_json, get_suppliers, get_customer, SelectCustomerView



urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='suppliers-list'),
    path('suppliers/new', views.SupplierCreateView.as_view(), name='new-supplier'),
    path('suppliers/<pk>/edit', views.SupplierUpdateView.as_view(), name='edit-supplier'),
    path('suppliers/<pk>/delete', views.SupplierDeleteView.as_view(), name='delete-supplier'),
    path('suppliers/<name>', views.SupplierView.as_view(), name='supplier'),
    path('supplier/<int:pk>/json/', supplier_detail_json, name='supplier-detail'),

    path('purchases/', views.PurchaseView.as_view(), name='purchases-list'),
    # path('purchases/new', views.SelectSupplierView.as_view(), name='select-supplier'),
    path('select-supplier/', views.SelectSupplierView.as_view(), name='select-supplier'),
    path('get-suppliers/<int:category_id>/', get_suppliers, name='get-suppliers'),
    path('purchases/new/<pk>', views.PurchaseCreateView.as_view(), name='new-purchase'),
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    path('get-stocks/', views.get_stocks, name='get_stocks'),
    path('get-stocks-purchase/', views.get_stocks_purchase, name='get_stocks_purchase'),
    path('get_stock_quantity/', views.get_stock_quantity, name='get_stock_quantity'),
    path('purchases/<pk>/delete', views.PurchaseDeleteView.as_view(), name='delete-purchase'),

    path('sales/', views.SaleView.as_view(), name='sales-list'),
    # path('select-customer/', views.SelectCustomerView.as_view(), name='select-customer'),
    # path('get-customers/<int:category_id>/', get_customer, name='get-customers'),

    path('get-customers/<str:cust_type>/', get_customer, name='get_customers'),
    path('select-customer/', views.SelectCustomerView.as_view(), name='select_customer'),
    path('select-customer_bill/', views.SelectCustomerView_bill.as_view(), name='select_customer_bill'),
    path('sales/new/<pk>', views.SaleCreateView.as_view(), name='new-sale'),
    path('sales/new_bill/<pk>', views.SaleCreateView_bill.as_view(), name='new-sale_bill'),

    path('sales/custome/<pk>', views.customeView.as_view(), name='custome-sale'),
    path('get-favoritelist-stocks/', views.get_favoritelist_stocks, name='get_favoritelist_stocks'),

    path('sales/new1/', views.SaleCreateView1.as_view(), name='new-sale1'),
    path('sales/<pk>/delete', views.SaleDeleteView.as_view(), name='delete-sale'),


    path('get-serial-numbers/', views.get_serial_numbers, name='get_serial_numbers'),
    path('update-sales-billno/', views.update_sales_billno, name='update_sales_billno'),
    # path('submit-purchase-form/', views.submit_purchase_form, name='submit_purchase_form'),


    # Genrate Purchase Bill
    path("purchases/<billno>", views.PurchaseBillView.as_view(), name="purchase-bill"),
    # path("sales/<billno>", views.SaleBillView.as_view(), name="sale-bill"),
    # Genrate Sales bill without show payment or GST
    path('sales/bill/<int:billno>/', views.SaleBillView.as_view(), name='sale-bill'),  # Ensure this is correct
    # Genrate Sales Bill with Payment & GST
    path('sales/bill/<int:billno>/', views.SaleBillView_bill.as_view(), name='sale-bill_bill'),  # Ensure this is correct
    # Genrate Return Bill
    path('return/bill/<int:billno>/', views.ReturnBillView.as_view(), name='return-bill'),  # Ensure this is correct
    # Genrate Final sales, Return, And Final all bill
    path('sales/salesbill/<int:billno>/', views.FinalSaleBillView.as_view(), name='final-sale-bill'),  # Ensure this is correct
    path('sales/returnbill/<int:billno>/', views.FinalReturnBillView.as_view(), name='final-return-bill'),  # Ensure this is correct
    path('sales/genratefinalbill/<int:billno>/', views.GenrateFinalBillView.as_view(), name='generate-final-bill'),  # Ensure this is correct



    path('sales/edit_sale/<int:pk>/', views.edit_sale_view, name='edit_sale'),
    path('get-serial-numbers_edit/', views.get_serial_numbers_edit, name='get_serial_numbers_edit'),
    path('update-sales-billno_edit/', views.update_sales_billno_edit, name='update_sales_billno_edit'),

    # return_sale html page is used for create Final Sales Bill
    path('sales/return_sale/', views.merge_sales_bill, name='merge_sales_bill'),
    path('get-customer-bills/', views.get_customer_bills, name='get_customer_bills'),
    path('generate-final-bill/', views.generate_final_bill, name='generate_final_bill'),

    path('finalsales/', views.FinalSaleView.as_view(), name='finalsales-list'),
    # path('sales/<pk>/delete_final_sale', views.FinalSaleDeleteView.as_view(), name='delete-final-sale'),
    path('sales/<int:pk>/delete_final_sale/', views.FinalSaleDeleteView.as_view(), name='delete-final-sale'),
    # path('sales/finalbill/<int:billno>/', views.FinalSaleBillView.as_view(), name='final-sale-bill'),  # Ensure this is correct


    # URL to render the edit sale page
    # path('sales/edit_finalsale/', views.merge_sales_bill1, name='edit_finalsale'),
    #
    # # URL to update and merge bills
    # path('sales/update_merge_bills/', views.update_and_merge_bills, name='update_and_merge_bills'),

    path("sales/edit_finalsale/<int:billno>/", views.edit_final_sale, name="edit_final_sale"),
    path("update-final-bill/", views.update_final_bill, name="update_final_bill"),

    # path('sales/select-return-customer/', views.SelectReturnCustomerView.as_view(), name='select_return_customer'),

    # # path('return_sale/<int:pk>/', views.return_sale_view, name='return_sale_view'),
    # path('sales/select_return_customer/', views.select_customer, name='select_customer_page'),
    # path('api/get_billnos/', views.get_billnos, name='get_billnos'),


    path('sales/sales_finalsales_return/<int:pk>/', views.return_sale_view, name='sales_finalsale_return'),

    path('sales/finalsales_return_edit/<int:pk>/', views.return_sale_view_edit, name='finalsales_return_edit'),
    path('final-get-serial-numbers_edit/', views.final_get_serial_numbers_edit, name='final_get_serial_numbers_edit'),
    # path('sales/return_sale/', views.bill_merge_view, name='return_sale'),
    # path('sales/get_bills/<int:customer_id>/', views.get_bills, name='get_bills'),


    # Genrate Return Bill
    path('return/select_customer/', views.select_customer_view, name='return_select_customer'),
    path('get_customers_by_type/<str:customer_type>/', views.get_customers_by_type, name='get_customers_by_type'),
    path('get_categories_by_billno/<str:billno>/', views.get_categories_by_billno, name='get_categories_by_billno'),
    path('get_billnos/<int:customer_id>/', views.get_billnos, name='get_billnos'),
    path('final-return-serial-numbers/', views.final_return_serial_numbers, name='final_return_serial_numbers'),
    path('return/finalsales_return/<int:pk>/', views.finalsale_return, name='finalsales_return'),

    # Return Edit Page
    path('return/return_edit/<int:pk>/', views.return_view_edit, name='return_edit'),

    # Return List
    path('return/returnsales/', views.ReturnSaleView.as_view(), name='returnsales-list'),




    # path('sales/return_sale/', views.get_customer_bills, name='return_sale'),
    # path('generate_final_bill/', views.generate_final_bill, name='generate_final_bill'),

    # path('merge_bills/', views.bill_merge_view, name='merge_bills'),
    # path('get_bills/<int:customer_id>/', views.get_bills, name='get_bills'),


    # path('sales/return_sale/', views.bill_merge_view, name='merge_sales_bill'),
    # path('sales/get_bills/<int:customer_id>/', views.get_bills, name='get_bills'),
    # path('sales/merge_bills/', views.bill_merge_view, name='merge_bills'),

    # path('sales/return_sale/', views.customer_bills, name='customer_bills'),
    # path('sales/get_bills_for_customer/<int:customer_id>/', views.get_bills_for_customer, name='get_bills_for_customer'),
    # path('generate_final_bill/', views.generate_final_bill, name='generate_final_bill'),
    #
    # path('sales/return_sale/', views.sale_bill_management, name='sale_bill_management'),


    # path('sales/return_sale/', views.sale_bill_management, name='sale_bill_management'),
    # # path('get-customer-bills/', views.get_customer_bills, name='get_customer_bills'),
    # # path('get_bills/<int:customer_id>/', views.get_bills, name='get_bills'),
    # path('get-customer-bills/', views.get_customer_bills, name='get_customer_bills'),

    # path('merge-sales-bill/', views.merge_sales_bill, name='merge_sales_bill'),
    # path('get-customer-bills/', views.get_customer_bills, name='get_customer_bills'),
    # path('generate-final-bill/', views.generate_final_bill, name='generate_final_bill'),

]