"""
User app URL configuration
"""
from django.urls import path
from . import views
from . import control_panel_views

app_name = 'user'

urlpatterns = [
    # Control Panel URLs
    path('control-panel/login/', control_panel_views.control_panel_login, name='control_panel_login'),
    path('control-panel/', control_panel_views.control_panel_home, name='control_panel_home'),
    path('control-panel/permissions/', control_panel_views.control_panel_permissions, name='control_panel_permissions'),
    path('control-panel/user/<int:user_id>/permissions/', control_panel_views.control_panel_user_permissions, name='control_panel_user_permissions'),
    path('control-panel/update-password/', control_panel_views.control_panel_update_password, name='control_panel_update_password'),
    path('control-panel/logout/', control_panel_views.control_panel_logout, name='control_panel_logout'),
    path('control-panel/save-permissions/<int:user_id>/', control_panel_views.control_panel_save_permissions, name='control_panel_save_permissions'),
    path('control-panel/initialize/', control_panel_views.initialize_modules_permissions, name='control_panel_initialize'),
    path(
        'control-panel/vendors/<int:vendor_id>/create-login/',
        control_panel_views.control_panel_create_vendor_user,
        name='control_panel_create_vendor_user',
    ),

    # Login routing + vendor portal
    path('post-login/', views.post_login_redirect, name='post_login_redirect'),
    path('no-access/', views.no_access, name='no_access'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor-dashboard'),
]
