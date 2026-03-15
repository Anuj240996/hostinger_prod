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

from product.views import get_subcategories
from transactions.views import get_stocks
from . import views
from .views import FavoriteListView

# from .views import StockListView, get_all_stocks, get_stocks_by_filter

# from .views import get_company_data, check_company_name, check_username


urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    # path('get-all-stocks/', views.get_all_stocks, name='get-all-stocks'),
    path('new/', views.StockCreateView.as_view(), name='new-stock'),
    path('stock/<pk>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<pk>/delete', views.StockDeleteView.as_view(), name='delete-stock'),
    # path('stocks/', views.StockListView.as_view(), name='stock-list'),
    # path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get-subcategories'),
    # path('get-stocks/<int:subcategory_id>/', views.get_stocks, name='get-stocks'),
    #
    # path('get-stocks/<str:filter_type>/', views.get_stocks_by_filter, name='get_stocks_by_filter'),
    # path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    # path('get-stocks/<int:subcategory_id>/', views.get_stocks, name='get_stocks'),
    # path('get-all-stocks/', views.get_all_stocks, name='get_all_stocks'),

    path('get-stocks-all/<str:filter_type>/', views.get_stocks_by_all, name='get_stocks_by_filter'),
    path('get-stocks/<str:filter_type>/category/<int:category_id>/', views.get_stocks_by_filter, name='get_stocks_by_category'),
    path('get-stocks/<str:filter_type>/<int:subcategory_id>/', views.get_stocks_by_filter, name='get_stocks_by_subcategory'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),

    path('favorite/', views.StockListView1.as_view(), name='favorite'),
    # path('', StockListView.as_view(), name='stock_list'),
    # path('create-favorite-list/', views.create_favorite_list, name='create_favorite_list'),
    # path('get-stocks-all/', views.get_stocks_all, name='get_stocks'),

    # path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    # path('get-stocks-all/', views.get_stocks, name='get_stocks'),

    # below url for create the favorite list
    path('get-stocks-all/', views.get_stocks_all, name='get_stocks_all'),
    path('get-subcategories1/', views.get_subcategories1, name='get_subcategories1'),
    path('create-favorite-list/', views.create_favorite_list, name='create_favorite_list'),

    path('favorite_list/', views.FavoriteListView.as_view(), name='favorite_list_view'),
    # path('favorite-lists/', FavoriteListView.as_view(), name='favorite_list_view'),
    path('favorite-list-details/<int:favorite_list_id>/', views.favorite_list_details, name='favorite_list_details'),
    # path('get-favorite-list/<int:favorite_list_id>/', views.get_favorite_list, name='get-favorite-list'),
    # path('get-favorite-list/', views.get_favorite_list, name='get_favorite_list'),

    path('edit-favorite/<int:favorite_id>/', views.edit_favorite_list, name='edit_favorite_list'),
    # path('update-favorite-stock-list/<int:favorite_list_id>/', views.update_favorite_stock_list, name='update_favorite_stock_list'),
    path('get_subcategories_edit/', views.get_subcategories_edit, name='get_subcategories_edit'),
    path('get_stocks_edit/', views.get_stocks_edit, name='get_stocks_edit'),
    path('get_stock_quantity/', views.get_stock_quantity, name='get_stock_quantity'),
    path('get_stock_detail/', views.get_stock_detail, name='get_stock_detail'),
    # path('remove-stock-from-favorite-list/<int:stock_id>/', views.remove_stock_from_favorite_list, name='remove_stock_from_favorite_list'),
    # path('remove-stock-from-favorite-list/<int:favorite_list_id>/<int:stock_id>/', views.remove_stock_from_favorite_list, name='remove_stock_from_favorite_list'),


    path('delete-favorite-list/<int:favorite_list_id>/', views.delete_favorite_list, name='delete_favorite_list'),
]

