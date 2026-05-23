from django.urls import path
from . import views

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    # path('create-from-survey/<int:survey_id>/', views.quotation_create_from_survey, name='quotation_create_from_survey'),
    path('create/', views.quotation_create, name='quotation_create'),
    path('<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path('<int:pk>/edit/', views.quotation_edit, name='quotation_edit'),
    path('<int:pk>/send/', views.quotation_send, name='quotation_send'),
    path('<int:pk>/approve/', views.quotation_approve, name='quotation_approve'),
    path('<int:pk>/mark-converted/', views.quotation_mark_converted, name='quotation_mark_converted'),
    path('<int:pk>/reject/', views.quotation_reject, name='quotation_reject'),
    path('<int:pk>/revise/', views.quotation_revise, name='quotation_revise'),
    path('<int:pk>/add-item/', views.add_quotation_item, name='add_quotation_item'),
    path('<int:pk>/add-note/', views.add_negotiation_note, name='add_negotiation_note'),
    path('<int:pk>/pdf/', views.quotation_pdf, name='quotation_pdf'),
    path('export/', views.quotation_export, name='quotation_export'),
]