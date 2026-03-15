from django.urls import path
from . import views

urlpatterns = [
    path('scrape/', views.scrape, name='scrape'),
]
