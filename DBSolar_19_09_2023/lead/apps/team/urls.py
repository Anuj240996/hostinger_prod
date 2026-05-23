from django.urls import path
from . import views

app_name = 'team'

urlpatterns = [
    path('', views.sales_team_dashboard, name='team'),
    path('<int:pk>/', views.sales_rep_detail, name='sales_rep_detail'),
    # path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),





    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]