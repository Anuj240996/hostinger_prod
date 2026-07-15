from django.contrib import admin
from django.urls import path
from firereport.views import *
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
#from user import views as user_views



urlpatterns = [
    #path('admin/', admin.site.urls),


    path('admin_login', admin_login, name='firereport-admin_login'),
    #path('', index, name='firereport-index'),
    path('reporting', reporting, name='firereport-reporting'),
    path('viewStatus', viewStatus, name='firereport-viewStatus'),
    path('viewStatusDetails/<int:pid>', viewStatusDetails, name='firereport-viewStatusDetails'),
    path('dashboard', dashboard, name='firereport-dashboard'),
    path('dashboard_staff', dashboard_staff, name='firereport-dashboard_staff'),
    path('addTeam', addTeam, name='firereport-addTeam'),
    path('manageTeam', manageTeam, name='firereport-manageTeam'),
    path('editTeam/<int:pid>', editTeam, name='firereport-editTeam'),
    path('deleteTeam/<int:pid>', deleteTeam, name='firereport-deleteTeam'),
    path('newRequest', newRequest, name='firereport-newRequest'),
    path('task', task, name='firereport-task'),

    path('assignRequest', assignRequest, name='firereport-assignRequest'),
    path('reassignRequest', reassignRequest, name='firereport-reassignRequest'),
    path('teamontheway', teamontheway, name='firereport-teamontheway'),
    path('workinprogress', workinprogress, name='firereport-workinprogress'),
    path('completeRequest', completeRequest, name='firereport-completeRequest'),
    path('allRequest', allRequest, name='firereport-allRequest'),
    path('deleteRequest/<int:pid>', deleteRequest, name='firereport-deleteRequest'),
    path('viewRequestDetails/<int:pid>', viewRequestDetails, name='firereport-viewRequestDetails'),
    path('reviewRequestDetails/<int:pid>', reviewRequestDetails, name='firereport-reviewRequestDetails'),
    path('dateReport', dateReport, name='firereport-dateReport'),
    path('search', search, name='firereport-search'),
    path('services/new', serviceRequestsNew, name='firereport-service-new'),
    path('services/assigned', serviceRequestsAssigned, name='firereport-service-assigned'),
    path('services/in-process', serviceRequestsInProcess, name='firereport-service-in-process'),
    path('services/completed', serviceRequestsCompleted, name='firereport-service-completed'),
    path('services/send-otp/<int:pid>', serviceSendReportOtp, name='firereport-service-send-otp'),
    path('services/verify-otp/<int:pid>', serviceVerifyReportOtp, name='firereport-service-verify-otp'),
    path('services/view/<int:pid>', serviceViewRequestDetails, name='firereport-service-viewRequestDetails'),
    path('services/report-pdf/<int:pid>', serviceReportPdf, name='firereport-service-report-pdf'),
    path('services/report-pdf/<int:pid>/', serviceReportPdf, name='firereport-service-report-pdf-slash'),
    path('services/remarks/add', serviceAddRemarkApi, name='firereport-service-add-remark-api'),
    path('services/start/<int:pid>', serviceMarkInProcess, name='firereport-service-mark-in-process'),
    path('services/complete/<int:pid>', serviceMarkCompleted, name='firereport-service-mark-completed'),
    path('changePassword', changePassword, name='firereport-changePassword'),
    path('logout/', Logout, name='firereport-logout'),
    path('get_profile_data/', get_profile_data, name='firereport-get_profile_data'),
    path('get_customer_details/', get_customer_details, name='firereport-get_customer_details'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
