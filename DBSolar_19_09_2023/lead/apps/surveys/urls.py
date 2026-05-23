from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('create/', views.survey_create, name='survey_create'),
    path('<int:pk>/', views.survey_detail, name='survey_detail'),
    path('<int:pk>/edit/', views.survey_edit, name='survey_edit'),
    path('<int:pk>/reschedule/', views.survey_reschedule, name='survey_reschedule'),
    path('<int:pk>/complete/', views.survey_complete, name='survey_complete'),
    path('<int:pk>/cancel/', views.survey_cancel, name='survey_cancel'),
    path('<int:pk>/upload-image/', views.upload_survey_image, name='upload_survey_image'),
    path('export/', views.survey_export, name='survey_export'),
]