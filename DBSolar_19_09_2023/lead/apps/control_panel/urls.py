# # from django.urls import path
# # from . import views
# #
# # app_name = 'control_panel'
# #
# # urlpatterns = [
# #     path('', views.dashboard, name='dashboard'),
# #     # Add other management views later (organizations, users, etc.)
# # ]
#
# from django.urls import path
# from . import views
#
# app_name = 'control_panel'
#
# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('organizations/', views.organizations, name='organizations'),
#     path('users/', views.users, name='users'),
#     path('roles/', views.roles, name='roles'),
#     path('subscriptions/', views.subscriptions, name='subscriptions'),
#     path('feature-flags/', views.feature_flags, name='feature_flags'),
# ]


from django.urls import path
from . import views

app_name = 'control_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('platform-dashboard/', views.platform_dashboard, name='platform_dashboard'),

    path('switch-org/<int:org_id>/', views.switch_organization, name='switch_organization'),
    path('clear-org-context/', views.clear_organization_context, name='clear_organization_context'),

    # Organizations
    # path('organizations/', views.organization_list, name='organizations'),  # if you have one
    path('organizations/', views.OrganizationListView.as_view(), name='organizations'),
    path('organizations/add/', views.OrganizationCreateView.as_view(), name='organization_add'),
    path('organizations/<int:pk>/edit/', views.OrganizationUpdateView.as_view(), name='organization_edit'),
    path('organizations/<int:pk>/delete/', views.OrganizationDeleteView.as_view(), name='organization_delete'),
    path('organization/<int:pk>/limits/', views.organization_limits, name='organization_limits'),
    path('organization/<int:pk>/', views.organization_detail, name='organization_detail'),


    # Users
    path('users/', views.UserListView.as_view(), name='users'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    # Roles
    path('roles/', views.RoleListView.as_view(), name='roles'),
    path('roles/add/', views.RoleCreateView.as_view(), name='role_add'),
    path('roles/<int:pk>/edit/', views.RoleUpdateView.as_view(), name='role_edit'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('roles/<int:pk>/permissions/', views.get_role_permissions, name='role_permissions_json'),
    path('roles/<int:pk>/permissions/update/', views.update_role_permissions, name='role_permissions_update'),

    # Subscriptions
    path('subscriptions/', views.SubscriptionPlanListView.as_view(), name='subscriptions'),
    path('subscriptions/plan/add/', views.SubscriptionPlanCreateView.as_view(), name='subscriptionplan_add'),
    path('subscriptions/plan/<int:pk>/edit/', views.SubscriptionPlanUpdateView.as_view(), name='subscriptionplan_edit'),
    path('subscriptions/plan/<int:pk>/delete/', views.SubscriptionPlanDeleteView.as_view(), name='subscriptionplan_delete'),
    path('subscriptions/assign/add/', views.OrganizationSubscriptionCreateView.as_view(), name='organizationsubscription_add'),
    path('subscriptions/assign/<int:pk>/edit/', views.OrganizationSubscriptionUpdateView.as_view(), name='organizationsubscription_edit'),
    path('subscriptions/assign/<int:pk>/delete/', views.OrganizationSubscriptionDeleteView.as_view(), name='organizationsubscription_delete'),

    # Feature Flags
    path('feature-flags/', views.FeatureListView.as_view(), name='feature_flags'),
    path('feature-flags/feature/add/', views.FeatureCreateView.as_view(), name='feature_add'),
    path('feature-flags/feature/<int:pk>/edit/', views.FeatureUpdateView.as_view(), name='feature_edit'),
    path('feature-flags/feature/<int:pk>/delete/', views.FeatureDeleteView.as_view(), name='feature_delete'),
    path('feature-flags/override/add/', views.OrganizationFeatureCreateView.as_view(), name='organizationfeature_add'),
    path('feature-flags/override/<int:pk>/edit/', views.OrganizationFeatureUpdateView.as_view(), name='organizationfeature_edit'),
    path('feature-flags/override/<int:pk>/delete/', views.OrganizationFeatureDeleteView.as_view(), name='organizationfeature_delete'),

    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_logs'),
]