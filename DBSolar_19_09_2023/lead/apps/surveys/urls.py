from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('create/', views.survey_create, name='survey_create'),
    path('<int:pk>/', views.survey_detail, name='survey_detail'),
    path('<int:pk>/edit/', views.survey_edit, name='survey_edit'),
    path('<int:pk>/reschedule/', views.survey_reschedule, name='survey_reschedule'),
    path('<int:pk>/complete/', views.survey_complete, name='survey_complete'),
    path('<int:pk>/report/', views.survey_report, name='survey_report'),
    path('<int:pk>/report/pdf/', views.survey_report_pdf, name='survey_report_pdf'),
    path('<int:pk>/structure-3d-embed/', views.survey_structure_3d_embed, name='survey_structure_3d_embed'),
    path('<int:pk>/cancel/', views.survey_cancel, name='survey_cancel'),
    path('<int:pk>/upload-image/', views.upload_survey_image, name='upload_survey_image'),
    path('export/', views.survey_export, name='survey_export'),
]