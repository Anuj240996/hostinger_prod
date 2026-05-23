# # # from django.contrib import admin
# # # from django.urls import path, include
# # # from django.conf import settings
# # # from django.conf.urls.static import static
# # # from django.contrib.auth import views as auth_views
# # # from debug_toolbar.toolbar import debug_toolbar_urls
# # #
# # # from apps.core.views import dashboard
# # #
# # # urlpatterns = [
# # #     # Admin
# # #     path('admin/', admin.site.urls),
# # #
# # #     # Dashboard
# # #     path('', dashboard, name='dashboard'),
# # #
# # #     # Leads
# # #     path('leads/', include('apps.leads.urls')),
# # #
# # #     # Authentication URLs
# # #     path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
# # #     path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
# # #     path('accounts/password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
# # #     path('accounts/password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
# # # ]
# # #
# # # # Serve media files in development
# # # if settings.DEBUG:
# # #     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# # #     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# # #     urlpatterns += debug_toolbar_urls()
# #
# # from django.contrib import admin
# # from django.urls import path, include
# # from django.conf import settings
# # from django.conf.urls.static import static
# # from django.contrib.auth import views as auth_views
# #
# # from apps.core.views import dashboard
# #
# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# #     path('', dashboard, name='dashboard'),
# #     path('leads/', include('apps.leads.urls')),
# #     path('pipeline/', include('apps.pipeline.urls')),
# #     path('surveys/', include('apps.surveys.urls')),
# #     path('quotations/', include('apps.quotations.urls')),
# #     path('revenue/', include('apps.revenue.urls')),
# #     path('analytics/', include('apps.analytics.urls')),
# #     path('team/', include('apps.team.urls')),
# #     path('settings/', include('apps.settings.urls')),
# #
# #     # Authentication
# #     path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
# #     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
# # ]
# #
# # if settings.DEBUG:
# #     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# #     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib.auth import views as auth_views
#
# from apps.core.views import dashboard
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', dashboard, name='dashboard'),
#     path('leads/', include('apps.leads.urls')),
#     path('pipeline/', include('apps.pipeline.urls')),
#     path('surveys/', include('apps.surveys.urls')),
#     path('quotations/', include('apps.quotations.urls')),
#     path('revenue/', include('apps.revenue.urls')),
#     path('analytics/', include('apps.analytics.urls')),
#     path('team/', include('apps.team.urls')),
#     path('settings/', include('apps.settings.urls')),
#
#     # Authentication
#     path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
#     path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib.auth import views as auth_views
#
# from apps.core.views import dashboard
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', dashboard, name='dashboard'),
#     path('leads/', include('apps.leads.urls')),
#     path('pipeline/', include('apps.pipeline.urls')),
#     path('surveys/', include('apps.surveys.urls')),
#     path('quotations/', include('apps.quotations.urls')),
#     path('revenue/', include('apps.revenue.urls')),
#     path('analytics/', include('apps.analytics.urls')),
#     path('team/', include('apps.team.urls')),
#     path('settings/', include('apps.settings.urls')),
#
#     # Authentication
#     path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
#     path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
# ]
#
# # Serve media and static files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from apps.core.views import dashboard, main_project_dashboard
from apps.core.views import OrganizationWizard


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('main-dashboard/', main_project_dashboard, name='main_project_dashboard'),
    # path('register/', include(OrganizationWizard.urls())),
    path('register/', OrganizationWizard.as_view(), name='register'),
    path('control-panel/', include('apps.control_panel.urls')),


    # App URLs
    path('leads/', include('apps.leads.urls')),
    path('pipeline/', include('apps.pipeline.urls')),
    path('surveys/', include('apps.surveys.urls')),
    path('quotations/', include('apps.quotations.urls')),
    path('revenue/', include('apps.revenue.urls')),
    path('analytics/', include('apps.analytics.urls')),
    # path('team/', include('apps.team.urls')),
    path('team/', include('apps.team.urls', namespace='team')),
    path('settings/', include('apps.settings.urls')),

    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

# Serve media and static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)