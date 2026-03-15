# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token
# from .views import viewsets_dict, api_views_dict, CustomerLoginView, GetCustomerDetails

# # Initialize router
# router = DefaultRouter()

# # Register dynamic viewsets
# for viewset_name, viewset_class in viewsets_dict.items():
#     router.register(viewset_name, viewset_class, basename=viewset_name)

# # Define urlpatterns
# urlpatterns = [
#     path("", include(router.urls)),  # Auto-register all models' endpoints
#     path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
#     path("get-profile/", CustomerLoginView.as_view(), name="get-profile"),
#     path('customer-details/', GetCustomerDetails.as_view(), name='customer-details'),
# ]

# # Add dynamic API views for each model
# for model_name, view_class in api_views_dict.items():
#     urlpatterns.append(path(f'api/{model_name}/', view_class.as_view(), name=f'api_{model_name}'))


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import viewsets_dict, api_views_dict, CustomerLoginView, GetCustomerDetails, CustomerDataView

# Initialize router
router = DefaultRouter()

# Register dynamic viewsets
for viewset_name, viewset_class in viewsets_dict.items():
    #router.register(viewset_name, viewset_class)
    router.register(viewset_name, viewset_class, basename=viewset_name)

# Define urlpatterns
urlpatterns = [
    path("", include(router.urls)),  # Auto-register all models' endpoints
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path("get-profile/", CustomerLoginView.as_view(), name="get-profile"),
    path('customer-details/', GetCustomerDetails.as_view(), name='customer-details'),
    path('customer-data/', CustomerDataView.as_view(), name='customer-data'),

]

# Add dynamic API views for each model
for model_name, view_class in api_views_dict.items():
    urlpatterns.append(path(f'api/{model_name}/', view_class.as_view(), name=f'api_{model_name}'))

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token
# from .views import api_views_dict, CustomerLoginView, GetCustomerDetails
# from django.urls import path
# from .views import DynamicModelDataView

# dynamic_list_view = DynamicModelDataView.as_view({'get': 'list'})

# urlpatterns = [
#     path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
#     path("get-profile/", CustomerLoginView.as_view(), name="get-profile"),
#     path('customer-details/', GetCustomerDetails.as_view(), name='customer-details'),
#     path('<str:model_name>/', dynamic_list_view, name='dynamic-api'),
# ]

# # Add individual API views for each model
# for model_name, view_class in api_views_dict.items():
#     urlpatterns.append(path(f'api/{model_name}/', view_class.as_view(), name=f'api_{model_name}'))







