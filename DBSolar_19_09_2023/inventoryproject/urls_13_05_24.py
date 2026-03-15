"""inventoryproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from user.forms import UserLoginForm
from django.urls import path, include
from django.contrib.auth import views as auth_views
from user import views as user_views
from dashboard import views as dashboard_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from user.views import *

from user.views import profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('customer/', include('customer.urls')),
    path('firereport/', include('firereport.urls')),
   #path('photos/', include('photos.urls')),
    path('detect_barcodes/', include('detect_barcodes.urls')),
    path('generate_barcodes/', include('generate_barcodes.urls')),
    path('register/', user_views.register, name='user-register'),
    path('add/', user_views.add, name='user-add'),
    path('', auth_views.LoginView.as_view(template_name='user/login.html', authentication_form=UserLoginForm), name='user-login'),
    path('profile/', user_views.profile, name='user-profile'),
    path('edit_profile/', user_views.edit_profile, name='user-edit_profile'),
    path('profile_update/<int:pk>', user_views.profile_update,name='user-profile-update'),
    path('profile_updatepage/<int:pk>', user_views.profile_updatepage,name='user-profile-updatepage'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'),
         name='user-logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('notification_count', dashboard_views.notification_count, name='notification_count'),
    path('edit_pdf/', emp_pdf, name='edit_pdf'),
    # path('delete-user/<int:user_id>/', dashboard_views.delete_user, name='delete-user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)