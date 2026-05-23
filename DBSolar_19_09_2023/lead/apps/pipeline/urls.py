# # apps/pipeline/urls.py
# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.pipeline_view, name='pipeline'),
#     path('export/', views.pipeline_export, name='pipeline_export'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.pipeline_view, name='pipeline'),
    path('update-stage/<uuid:pk>/', views.update_lead_stage, name='update_lead_stage'),
    path('export/', views.pipeline_export, name='pipeline_export'),
]