from django.urls import path
# from django.conf.urls import url
from . import views
from .views import GetSubcategoriesView, filter_stock

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('get-subcategories/<int:category_id>/', GetSubcategoriesView.as_view(), name='get-subcategories'),
    path('filter-stock/', filter_stock, name='filter-stock'),
    # path('about/', views.AboutView.as_view(), name='about')
]