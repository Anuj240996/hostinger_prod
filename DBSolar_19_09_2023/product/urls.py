from django.contrib import admin
from django.urls import path
from firereport.views import *
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
#from user import views as user_views



# urlpatterns = [
    #path('admin/', admin.site.urls),

#
#     path('admin_login', admin_login, name='firereport-admin_login'),
#     #path('', index, name='firereport-index'),
#     path('reporting', reporting, name='firereport-reporting'),
#     path('viewStatus', viewStatus, name='firereport-viewStatus'),
#     path('viewStatusDetails/<int:pid>', viewStatusDetails, name='firereport-viewStatusDetails'),
#     path('dashboard', dashboard, name='firereport-dashboard'),
#     path('dashboard_staff', dashboard_staff, name='firereport-dashboard_staff'),
#     path('addTeam', addTeam, name='firereport-addTeam'),
#     path('manageTeam', manageTeam, name='firereport-manageTeam'),
#     path('editTeam/<int:pid>', editTeam, name='firereport-editTeam'),
#     path('deleteTeam/<int:pid>', deleteTeam, name='firereport-deleteTeam'),
#     path('newRequest', newRequest, name='firereport-newRequest'),
#     path('task', task, name='firereport-task'),
#
#     path('assignRequest', assignRequest, name='firereport-assignRequest'),
#     path('reassignRequest', reassignRequest, name='firereport-reassignRequest'),
#     path('teamontheway', teamontheway, name='firereport-teamontheway'),
#     path('workinprogress', workinprogress, name='firereport-workinprogress'),
#     path('completeRequest', completeRequest, name='firereport-completeRequest'),
#     path('allRequest', allRequest, name='firereport-allRequest'),
#     path('deleteRequest/<int:pid>', deleteRequest, name='firereport-deleteRequest'),
#     path('viewRequestDetails/<int:pid>', viewRequestDetails, name='firereport-viewRequestDetails'),
#     path('reviewRequestDetails/<int:pid>', reviewRequestDetails, name='firereport-reviewRequestDetails'),
#     path('dateReport', dateReport, name='firereport-dateReport'),
#     path('search', search, name='firereport-search'),
#     path('changePassword', changePassword, name='firereport-changePassword'),
#     path('logout/', Logout, name='firereport-logout'),
#     path('get_profile_data/', get_profile_data, name='firereport-get_profile_data'),
#     path('get_customer_details/', get_customer_details, name='firereport-get_customer_details'),
# ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path
from product import views



from django.urls import path
from . import views
# from .views import get_company_data, check_company_name, check_username


urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('admin/', admin.site.urls),
    # path('', views.product, name='product'),
    path('add_category/', views.add_category, name='product_add_category'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('get_category/<int:id>/', views.get_category, name='get_category'),
    path('get_subcategory/<int:id>/', views.get_subcategory, name='get_subcategory'),
    path('edit_category/<int:id>/', views.edit_category, name='edit_category'),
    path('product/update_subcategory/', views.update_subcategory, name='update_subcategory'),
    path('get_brand/<int:id>/', views.get_brand, name='get_brand'),
    path('get_unit/<int:id>/', views.get_unit, name='get_unit'),
    path('get_supplier/<int:id>/', views.get_supplier, name='get_supplier'),
    path('product/update_supplier/', views.update_supplier, name='update_supplier'),
    # path('get_product/<int:id>/', views.get_product, name='get_product'),
    path('get-product/<int:product_id>/', views.get_product, name='get_product'),
    path('product/update_product/', views.update_product, name='update_product'),
    path('delete_category/<int:id>/', views.delete_category, name='delete_category'),
    path('delete_subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('delete_brand/<int:id>/', views.delete_brand, name='delete_brand'),
    path('delete_unit/<int:id>/', views.delete_unit, name='delete_unit'),
    path('delete_supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),
    path('precheck-delete/<str:entity>/<int:id>/', views.precheck_delete_usage, name='precheck_delete_usage'),
    # path('edit-category/<int:id>/', views.edit_category, name='edit_category'),
    # path('edit-subcategory/<int:id>/', views.edit_subcategory, name='edit_subcategory'),
    # path('edit-product/<int:id>/', views.edit_product, name='edit_product'),
    # path('add-subcategory/', views.add_subcategory, name='product_add_subcategory'),
    # path('add-product/', views.add_product, name='product_add_product'),
    #
    # SubCategory URLs
    # path('edit_subcategory/<int:id>/', views.edit_subcategory, name='edit_subcategory'),
    # path('delete_subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    #
    # # Product URLs
    # path('products/edit/<int:pk>/', views.edit_product, name='edit-product'),
    # path('products/delete/<int:pk>/', views.delete_product, name='delete-product'),
    #
    # # Brand URLs
    # path('brands/edit/<int:pk>/', views.edit_brand, name='edit-brand'),
    # path('brands/delete/<int:pk>/', views.delete_brand, name='delete-brand'),
    #
    # # Unit URLs
    # path('units/edit/<int:pk>/', views.edit_unit, name='edit-unit'),
    # path('units/delete/<int:pk>/', views.delete_unit, name='delete-unit'),
    #
    # # Supplier URLs
    # path('suppliers/edit/<int:pk>/', views.edit_supplier, name='edit-supplier'),
    # path('suppliers/delete/<int:pk>/', views.delete_supplier, name='delete-supplier'),
]
