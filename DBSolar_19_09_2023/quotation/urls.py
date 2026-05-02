# from django.contrib import admin
# from django.urls import path
# from firereport.views import *
# from django.conf import settings
# from django.conf.urls.static import static
#
# from django.contrib.auth import views as auth_views
# #from user import views as user_views
#
# # quotation/urls.py
# from django.urls import path
# from . import views
#
# app_name = 'quotation'
#
# urlpatterns = [
#     path('quotations/', views.quotation_list, name='quotation_list'),
#     path('quotation/new/', views.create_quotation, name='create_quotation'),
#     path('quotation/<int:pk>/edit/', views.edit_quotation, name='edit_quotation'),
#     path('quotation/<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),
#
#
#     # New company creation pages
#     path('panel-company/new/', views.create_panel_company, name='create_panel_company'),
#     path('inverter-company/new/', views.create_inverter_company, name='create_inverter_company'),
#
# ]


from django.urls import path
from . import views

app_name = 'quotation'

urlpatterns = [
    path('quotations/', views.quotation_list, name='quotation_list'),
    path("confirm/<int:pk>/", views.confirm_quotation, name="confirm_quotation"),

    # New URLs for convert consumer functionality
    path('check-confirmed/<int:pk>/', views.check_quotation_confirmed, name='check_quotation_confirmed'),
    path('get-quotation-details/<int:pk>/', views.get_quotation_details, name='get_quotation_details'),
    path('store-quotation-data/', views.store_quotation_data, name='store_quotation_data'),

    # path('confirm/<int:quotation_id>/', views.confirm_quotation, name='confirm_quotation'),
    path('quotation/new/', views.create_quotation, name='create_quotation'),
    path('add_other_item/', views.add_other_item_api, name='add_other_item_api'),

    path('quotation/<int:pk>/edit/', views.edit_quotation, name='edit_quotation'),
    path('<int:pk>/revise/', views.revise_quotation, name='revise_quotation'),  # Add this line
    path('quotation/<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),

    # ✅ new company creation pages
    # path('panel-company/new/', views.create_panel_company, name='create_panel_company'),
    # path('inverter-company/new/', views.create_inverter_company, name='create_inverter_company'),
    path('api/add-panel-company/', views.add_panel_company_api, name='add_panel_company_api'),
    path('api/add-inverter-company/', views.add_inverter_company_api, name='add_inverter_company_api'),
    path('add-representative-api/', views.add_representative_api, name='add_representative_api'),
    path('update-representative-api/', views.update_representative_api, name='update_representative_api'),
    # NEW: Add plant capacity API
    path('api/add-plant-capacity/', views.add_plant_capacity_api, name='add_plant_capacity_api'),
    path('add-terms-condition/', views.add_terms_condition_api, name='add_terms_condition_api'),
    path('add-terms-api/', views.add_terms_api, name='add_terms_api'),
    path('check-consumer/', views.check_consumer, name='check_consumer'),
    # path('check-consumer-simple/', views.check_consumer_simple, name='check_consumer_simple'),
    # path("edit-model/", views.edit_any_model, name="edit_any_model"),
    path('<int:pk>/industrial_pdf/', views.industrial_quotation_pdf, name='industrial_quotation_pdf'),
    path('<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),


]
