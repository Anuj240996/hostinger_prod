from django.urls import path

from firereport.views import dashboard_staff
from . import views
from .views import toggle_status

urlpatterns = [
    path('index/', views.index, name='dashboard-index'),
    path('index1/', views.index1, name='dashboard-index1'),
    path('Administration/', views.Administration, name='dashboard-Administration'),
    path('Allstaff/', views.Allstaff, name='dashboard-Allstaff'),
    path('customers/', views.customers, name='dashboard-customers'),
    path('stockist/', views.stockist, name='dashboard-stockist'),
    path('finance/', views.finance, name='dashboard-finance'),
    path('engineers/', views.engineers, name='dashboard-engineers'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete-user'),
    path('toggle-status/<int:user_id>/<str:action>/', views.toggle_status, name='toggle_status'),
    path('customers/detail/<int:pk>/', views.customer_detail,name='dashboard-customer-detail'),
    path('sendstaff_Notification', views.staff_Send_Notification,name='dashboard-staff_Send_Notification'),
    path('sendconsumer_Notification', views.consumer_Send_Notification,name='dashboard-consumer_Send_Notification'),
    path('savestaff_Notification', views.save_staff_Notification, name='dashboard-save_staff_notification'),
    path('allnotification', views.allnotification, name='dashboard-allnotification'),
    path('allconsumernotification', views.allconsumernotification, name='dashboard-allconsumernotification'),
    path('Notification', views.Notification,name='dashboard-notification'),
    path('mark_as_done/<str:status>', views.Staff_Notification_Mark_Done, name='Staff_Notification_Mark_Done'),
    path('notification_count', views.notification_count, name='dashboard-notification_count'),
    path('dashboard_staff', dashboard_staff, name='dashboard-dashboard_staff'),
]
