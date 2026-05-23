# # from django.urls import path
# # from . import views
# #
# # urlpatterns = [
# #     path('', views.settings_dashboard, name='settings'),
# #
# #     # Lead Sources
# #     path('lead-source/add/', views.add_lead_source, name='add_lead_source'),
# #     path('lead-source/<int:pk>/edit/', views.edit_lead_source, name='edit_lead_source'),
# #     path('lead-source/<int:pk>/toggle/', views.toggle_lead_source, name='toggle_lead_source'),
# #
# #     # Lost Reasons
# #     path('lost-reason/add/', views.add_lost_reason, name='add_lost_reason'),
# #     path('lost-reason/<int:pk>/delete/', views.delete_lost_reason, name='delete_lost_reason'),
# #
# #     # Scoring Rules
# #     path('scoring-rule/add/', views.add_scoring_rule, name='add_scoring_rule'),
# #     path('scoring-rule/<int:pk>/edit/', views.edit_scoring_rule, name='edit_scoring_rule'),
# #     path('scoring-rule/<int:pk>/delete/', views.delete_scoring_rule, name='delete_scoring_rule'),
# #
# #     # Settings
# #     path('update/', views.update_setting, name='update_setting'),
# #
# #     path('pipeline-stage/add/', views.add_pipeline_stage, name='add_pipeline_stage'),
# #     path('pipeline-stage/<int:pk>/edit/', views.edit_pipeline_stage, name='edit_pipeline_stage'),
# #     path('pipeline-stage/<int:pk>/delete/', views.delete_pipeline_stage, name='delete_pipeline_stage'),
# # ]
# #
# # from django.urls import path
# # from . import views
# #
# # urlpatterns = [
# #     path('', views.settings_dashboard, name='settings'),
# #
# #     # Pipeline Stages
# #     path('pipeline-stage/add/', views.add_pipeline_stage, name='add_pipeline_stage'),
# #     path('pipeline-stage/<int:pk>/get/', views.get_pipeline_stage, name='get_pipeline_stage'),
# #     path('pipeline-stage/<int:pk>/edit/', views.edit_pipeline_stage, name='edit_pipeline_stage'),
# #     path('pipeline-stage/<int:pk>/delete/', views.delete_pipeline_stage, name='delete_pipeline_stage'),
# #
# #     # Lead Sources
# #     path('lead-source/add/', views.add_lead_source, name='add_lead_source'),
# #     path('lead-source/<int:pk>/edit/', views.edit_lead_source, name='edit_lead_source'),
# #     path('lead-source/<int:pk>/toggle/', views.toggle_lead_source, name='toggle_lead_source'),
# #
# #     # Campaigns
# #     path('campaign/add/', views.add_campaign, name='add_campaign'),
# #     path('campaign/<int:pk>/edit/', views.edit_campaign, name='edit_campaign'),
# #
# #     # Lost Reasons
# #     path('lost-reason/add/', views.add_lost_reason, name='add_lost_reason'),
# #     path('lost-reason/<int:pk>/delete/', views.delete_lost_reason, name='delete_lost_reason'),
# #
# #     # Scoring Rules
# #     path('scoring-rule/add/', views.add_scoring_rule, name='add_scoring_rule'),
# #     path('scoring-rule/<int:pk>/edit/', views.edit_scoring_rule, name='edit_scoring_rule'),
# #     path('scoring-rule/<int:pk>/delete/', views.delete_scoring_rule, name='delete_scoring_rule'),
# # ]
#
# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.settings_dashboard, name='settings'),
#
#     # Pipeline Stages
#     path('pipeline-stage/add/', views.add_pipeline_stage, name='add_pipeline_stage'),
#     path('pipeline-stage/<int:pk>/get/', views.get_pipeline_stage, name='get_pipeline_stage'),
#     path('pipeline-stage/<int:pk>/edit/', views.edit_pipeline_stage, name='edit_pipeline_stage'),
#     path('pipeline-stage/<int:pk>/delete/', views.delete_pipeline_stage, name='delete_pipeline_stage'),
#
#     # Lead Sources
#     path('lead-source/add/', views.add_lead_source, name='add_lead_source'),
#     path('lead-source/<int:pk>/edit/', views.edit_lead_source, name='edit_lead_source'),
#     # path('lead-source/<int:pk>/toggle/', views.toggle_lead_source, name='toggle_lead_source'),
#     path('lead-source/<int:pk>/get/', views.get_lead_source, name='get_lead_source'),
#     path('lead-source/<int:pk>/delete/', views.delete_lead_source, name='delete_lead_source'),
#
#     # Campaigns
#     path('campaign/add/', views.add_campaign, name='add_campaign'),
#     path('campaign/<int:pk>/edit/', views.edit_campaign, name='edit_campaign'),
#
#     # Lost Reasons
#     path('lost-reason/add/', views.add_lost_reason, name='add_lost_reason'),
#     path('lost-reason/<int:pk>/delete/', views.delete_lost_reason, name='delete_lost_reason'),
#
#     # Scoring Rules
#     path('scoring-rule/add/', views.add_scoring_rule, name='add_scoring_rule'),
#     path('scoring-rule/<int:pk>/edit/', views.edit_scoring_rule, name='edit_scoring_rule'),
#     path('scoring-rule/<int:pk>/delete/', views.delete_scoring_rule, name='delete_scoring_rule'),
#
#     # Roles
#     path('role/add/', views.add_role, name='add_role'),
#     path('role/<int:pk>/edit/', views.edit_role, name='edit_role'),
#     path('role/<int:pk>/permissions/', views.get_role_permissions, name='get_role_permissions'),
#     path('role/<int:pk>/permissions/update/', views.update_role_permissions, name='update_role_permissions'),
# ]


from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_dashboard, name='settings'),

    # Pipeline Stages
    path('pipeline-stage/add/', views.add_pipeline_stage, name='add_pipeline_stage'),
    path('pipeline-stage/<int:pk>/get/', views.get_pipeline_stage, name='get_pipeline_stage'),
    path('pipeline-stage/<int:pk>/edit/', views.edit_pipeline_stage, name='edit_pipeline_stage'),
    path('pipeline-stage/<int:pk>/delete/', views.delete_pipeline_stage, name='delete_pipeline_stage'),

    # Lead Sources
    path('lead-source/<int:pk>/get/', views.get_lead_source, name='get_lead_source'),
    path('lead-source/add/', views.add_lead_source, name='add_lead_source'),
    path('lead-source/<int:pk>/edit/', views.edit_lead_source, name='edit_lead_source'),
    path('lead-source/<int:pk>/toggle/', views.toggle_lead_source, name='toggle_lead_source'),
    path('lead-source/<int:pk>/delete/', views.delete_lead_source, name='delete_lead_source'),

    # Campaigns
    path('campaign/add/', views.add_campaign, name='add_campaign'),
    path('campaign/<int:pk>/get/', views.get_campaign, name='get_campaign'),
    path('campaign/<int:pk>/edit/', views.edit_campaign, name='edit_campaign'),

    # Lost Reasons
    path('lost-reason/add/', views.add_lost_reason, name='add_lost_reason'),
    path('lost-reason/<int:pk>/delete/', views.delete_lost_reason, name='delete_lost_reason'),

    # Scoring Rules
    path('scoring-rule/add/', views.add_scoring_rule, name='add_scoring_rule'),
    path('scoring-rule/<int:pk>/get/', views.get_scoring_rule, name='get_scoring_rule'),
    path('scoring-rule/<int:pk>/edit/', views.edit_scoring_rule, name='edit_scoring_rule'),
    path('scoring-rule/<int:pk>/delete/', views.delete_scoring_rule, name='delete_scoring_rule'),

    # Roles
    path('role/add/', views.add_role, name='add_role'),
    path('role/<int:pk>/edit/', views.edit_role, name='edit_role'),
    path('role/<int:pk>/permissions/', views.get_role_permissions, name='get_role_permissions'),
    path('role/<int:pk>/permissions/update/', views.update_role_permissions, name='update_role_permissions'),
]