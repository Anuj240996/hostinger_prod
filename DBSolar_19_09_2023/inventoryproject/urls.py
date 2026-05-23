# """inventoryproject URL Configuration

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/3.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from user.forms import UserLoginForm
# from django.urls import path, include
# from django.contrib.auth import views as auth_views
# from user import views as user_views
# from dashboard import views as dashboard_views
# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import include, path
# from user.views import *

# from user.views import profile

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('dashboard.urls')),
#     path('customer/', include('customer.urls')),
#     path('firereport/', include('firereport.urls')),
#   #path('photos/', include('photos.urls')),
#     path('detect_barcodes/', include('detect_barcodes.urls')),
#     path('generate_barcodes/', include('generate_barcodes.urls')),
#     path('register/', user_views.register, name='user-register'),
#     path('add/', user_views.add, name='user-add'),
#     # path('permission_form/', user_views.permission_form, name='user-permission_form'),

#     # Include Django's authentication URLs
#     path('accounts/', include('django.contrib.auth.urls')),
#     path('', auth_views.LoginView.as_view(template_name='user/login.html', authentication_form=UserLoginForm), name='user-login'),
#     #path('login/', CustomLoginView.as_view(), name='user-login'),
#     # path('change-password/', change_password_view, name='user-change_password_view'),
#     path('profile/', user_views.profile, name='user-profile'),
#     path('edit_profile/', user_views.edit_profile, name='user-edit_profile'),
#     path('profile_update/<int:pk>', user_views.profile_update,name='user-profile-update'),
#     path('profile_updatepage/<int:pk>', user_views.profile_updatepage,name='user-profile-updatepage'),
#     path('logout/', auth_views.LogoutView.as_view(template_name='user/logout.html'),
#          name='user-logout'),

#     path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='user/password_reset_form.html'), name='password_reset_form'),
#     path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
#     path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
#     path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'), name='password_reset_complete'),

#     path('notification_count', dashboard_views.notification_count, name='notification_count'),
#     path('edit_pdf/', emp_pdf, name='edit_pdf'),
#     # path('delete-user/<int:user_id>/', dashboard_views.delete_user, name='delete-user'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.MEDIA_URL,
#                       document_root=settings.MEDIA_ROOT)



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
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from user import views as user_views
from dashboard import views as dashboard_views
from django.conf import settings
from django.conf.urls.static import static
from user.views import *
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import never_cache

from user.views import profile
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.generic import RedirectView

from inventoryproject.legacy_redirects import redirect_legacy_leads_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('quotation/', include('quotation.urls')),
    # Legacy /leads/* URLs → integrated CRM (old leads app removed)
    path('leads/create/', RedirectView.as_view(url='/new-lead/leads/create/', permanent=False), name='lead_create'),
    path('leads/', RedirectView.as_view(url='/new-lead/leads/', permanent=False)),
    re_path(r'^leads/(?P<subpath>.+)/$', redirect_legacy_leads_path),
    path('new-lead/', include('crm.urls')),
    path('customer/', include('customer.urls')),
    path('firereport/', include('firereport.urls')),
   #path('photos/', include('photos.urls')),
    path('detect_barcodes/', include('detect_barcodes.urls')),
    path('generate_barcodes/', include('generate_barcodes.urls')),
    path('product/', include('product.urls')),
    path('inventory/', include('inventory.urls')),
    path('transactions/', include('transactions.urls')),
    path('homepage/', include('homepage.urls')),
    path('register/', user_views.register, name='user-register'),
    path('add/', user_views.add, name='user-add'),
    path('permission_form/', user_views.permission_form, name='user-permission_form'),
    path('user/', include('user.urls')),  # Include user app URLs (includes control panel)
    path('api/', include('api.urls')),

    # Include Django's authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    path('', never_cache(auth_views.LoginView.as_view(template_name='user/login.html', authentication_form=UserLoginForm)), name='user-login'),
    #path('login/', CustomLoginView.as_view(), name='user-login'),
    # path('change-password/', change_password_view, name='user-change_password_view'),
    path('profile/', user_views.profile, name='user-profile'),
    path('edit_profile/', user_views.edit_profile, name='user-edit_profile'),
    path('profile_update/<int:pk>', user_views.profile_update,name='user-profile-update'),
    path('profile_updatepage/<int:pk>', user_views.profile_updatepage,name='user-profile-updatepage'),
    path('logout/', user_views.logout_view, name='user-logout'),


    path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='user/password_reset_form.html'), name='password_reset_form'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'), name='password_reset_complete'),

    path('notification_count', dashboard_views.notification_count, name='notification_count'),
    path('edit_pdf/', emp_pdf, name='edit_pdf'),
    # path('delete-user/<int:user_id>/', dashboard_views.delete_user, name='delete-user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)