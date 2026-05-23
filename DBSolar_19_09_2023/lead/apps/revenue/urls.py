from django.urls import path
from . import views

urlpatterns = [
    path('', views.revenue_dashboard, name='revenue'),
    path('add/', views.add_revenue, name='add_revenue'),
    path('export/', views.revenue_export, name='revenue_export'),
    path('<int:pk>/mark-paid/', views.mark_revenue_paid, name='mark_revenue_paid'),
]