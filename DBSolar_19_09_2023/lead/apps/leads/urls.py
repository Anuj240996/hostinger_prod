from django.urls import path
from . import views

urlpatterns = [
    path('', views.lead_list, name='lead_list'),
    path('create/', views.lead_create, name='lead_create'),
    path('<uuid:pk>/', views.lead_detail, name='lead_detail'),
    path('<uuid:pk>/edit/', views.lead_edit, name='lead_edit'),
    path('<uuid:pk>/update-stage/', views.lead_update_stage, name='lead_update_stage'),
    path('<uuid:pk>/mark-lost/', views.lead_mark_lost, name='lead_mark_lost'),
    path('<uuid:pk>/add-activity/', views.lead_add_activity, name='lead_add_activity'),
    path('export/', views.lead_export, name='lead_export'),
]