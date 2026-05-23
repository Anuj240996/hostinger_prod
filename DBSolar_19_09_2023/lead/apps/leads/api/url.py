from django.urls import path
from ..views import lead_list, lead_detail

urlpatterns = [
    path('leads/', lead_list, name='api_lead_list'),
    path('leads/<uuid:pk>/', lead_detail, name='api_lead_detail'),
]