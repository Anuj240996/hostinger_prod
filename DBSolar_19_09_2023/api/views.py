# from django.contrib.auth import authenticate
# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from django.apps import apps
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User
# from django.urls import path
# from .models import *
# from .serializers import serializers_dict, CustomerSerializer, CustomerMsebSerializer

# # Dictionary to store dynamically generated viewsets and API views
# viewsets_dict = {}
# api_views_dict = {}

# # Fetch all models from this Django app
# all_models = list(apps.get_app_config('api').get_models())  # Replace 'api' with your actual app name

# # Dynamically create viewsets for each model
# for model in all_models:
#     serializer_class = serializers_dict.get(model.__name__)

#     if serializer_class:
#         class DynamicFilteredViewSet(viewsets.ModelViewSet):
#             authentication_classes = [TokenAuthentication]
#             permission_classes = [IsAuthenticated]
#             serializer_class = serializer_class

#             def get_queryset(self):
#                 user = self.request.user
#                 auth_user = AuthUser.objects.filter(id=user.id).first()
#                 if not auth_user:
#                     return model.objects.none()  # No data if user not found

#                 customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
#                 if not customer:
#                     return model.objects.none()  # No data if customer not found

#                 # Return filtered data based on the logged-in customer
#                 if hasattr(model, 'customer'):
#                     return model.objects.filter(customer_id=customer.cust_id)
#                 return model.objects.none()

#         viewsets_dict[model.__name__.lower()] = DynamicFilteredViewSet

#         # Create individual API views for each model
#         #
#         class DynamicCustomerDataView(APIView):
#             authentication_classes = [TokenAuthentication]
#             permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user
#             print(f"Authenticated User: {user.username}")  # Debug log

#             auth_user = AuthUser.objects.filter(id=user.id).first()
#             if not auth_user:
#                 print("AuthUser not found")  # Debug log
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
#             if not customer:
#                 print("Customer not found")  # Debug log
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             print(f"Customer ID: {customer.cust_id}")  # Debug log

#             queryset = model.objects.filter(customer_id=customer.cust_id)
#             print(f"Queryset: {queryset}")  # Debug log

#             serializer = serializer_class(queryset, many=True)
#             print(f"Serialized Data: {serializer.data}")  # Debug log

#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             print(f"Error: {str(e)}")  # Debug log
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def secured_view(request):
#     return Response({"message": "This is a secured API"})

# # Custom Login View
# class CustomerLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         if not username or not password:
#             return Response(
#                 {"error": "Please provide both username and password."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = authenticate(username=username, password=password)

#         if user:
#             try:
#                 auth_user = AuthUser.objects.get(username=user.username)
#             except AuthUser.DoesNotExist:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             token, _ = Token.objects.get_or_create(user=user)

#             try:
#                 customer = Customer.objects.get(new_customer=auth_user)
#                 customer_serializer = CustomerSerializer(customer)
#             except Customer.DoesNotExist:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             return Response(
#                 {
#                     "token": token.key,
#                     "user": {
#                         "username": auth_user.username,
#                         "email": auth_user.email,
#                         "customer_details": customer_serializer.data,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"error": "Invalid username or password."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

# class GetCustomerDetails(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user

#             auth_user = AuthUser.objects.filter(username=user.username).first()
#             if not auth_user:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer = Customer.objects.filter(new_customer=auth_user).first()
#             if not customer:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer_serializer = CustomerSerializer(customer)
#             return Response(
#                 {"customer_details": customer_serializer.data},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.apps import apps
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.urls import path
#from .models import *
from .serializers import serializers_dict, CustomerSerializer #, CustomerMsebSerializer
from .models import AuthUser, Customer, CustomerMseb

# Dictionary to store dynamically generated viewsets and API views
viewsets_dict = {}
api_views_dict = {}

# Fetch all models from this Django app
all_models = list(apps.get_app_config('api').get_models())  # Replace 'api' with your actual app name

# Dynamically create viewsets for each model
for model in all_models:
    serializer_class = serializers_dict.get(model.__name__)

    if serializer_class:
        class DynamicFilteredViewSet(viewsets.ModelViewSet):
            authentication_classes = [TokenAuthentication]
            permission_classes = [IsAuthenticated]
            serializer_class = serializer_class

            def get_queryset(self):
                user = self.request.user
                auth_user = AuthUser.objects.filter(id=user.id).first()
                if not auth_user:
                    return model.objects.none()  # No data if user not found

                customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
                if not customer:
                    return model.objects.none()  # No data if customer not found

                # Return filtered data based on the logged-in customer
                if hasattr(model, 'customer'):
                    return model.objects.filter(customer_id=customer.cust_id)
                return model.objects.none()

        viewsets_dict[model.__name__.lower()] = DynamicFilteredViewSet

        # Create individual API views for each model
        class DynamicCustomerDataView(APIView):
            authentication_classes = [TokenAuthentication]
            permission_classes = [IsAuthenticated]

            def get(self, request, *args, **kwargs):
                try:
                    user = request.user
                    auth_user = AuthUser.objects.filter(id=user.id).first()
                    if not auth_user:
                        return Response(
                            {"error": "User not found in AuthUser table."},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
                    if not customer:
                        return Response(
                            {"error": "Customer profile not found for this user."},
                            status=status.HTTP_404_NOT_FOUND,
                        )

                    queryset = model.objects.filter(customer_id=customer.cust_id)
                    serializer = serializer_class(queryset, many=True)

                    return Response(serializer.data, status=status.HTTP_200_OK)

                except Exception as e:
                    return Response(
                        {"error": f"An unexpected error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        api_views_dict[model.__name__.lower()] = DynamicCustomerDataView



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def secured_view(request):
    return Response({"message": "This is a secured API"})


# Custom Login View
class CustomerLoginView(APIView):
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user:
            try:
                auth_user = AuthUser.objects.get(username=user.username)
            except AuthUser.DoesNotExist:
                return Response(
                    {"error": "User not found in AuthUser table."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            token, _ = Token.objects.get_or_create(user=user)

            try:
                customer = Customer.objects.get(new_customer=auth_user)
                customer_serializer = CustomerSerializer(customer)
            except Customer.DoesNotExist:
                return Response(
                    {"error": "Customer profile not found for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {
                    "token": token.key,
                    "user": {
                        "username": auth_user.username,
                        "email": auth_user.email,
                        "customer_details": customer_serializer.data,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class GetCustomerDetails(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            auth_user = AuthUser.objects.filter(username=user.username).first()
            if not auth_user:
                return Response(
                    {"error": "User not found in AuthUser table."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            customer = Customer.objects.filter(new_customer=auth_user).first()
            if not customer:
                return Response(
                    {"error": "Customer profile not found for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            customer_serializer = CustomerSerializer(customer)
            return Response(
                {"customer_details": customer_serializer.data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomerDataView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            # Fetch the AuthUser instance associated with the authenticated user
            auth_user = AuthUser.objects.filter(id=user.id).first()
            if not auth_user:
                return Response(
                    {"error": "User not found in AuthUser table."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch the Customer instance where `new_customer` is the authenticated user
            customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
            if not customer:
                return Response(
                    {"error": "Customer profile not found for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch data from all models related to the customer
            data = {}
            for model in all_models:
                if hasattr(model, 'customer'):
                    queryset = model.objects.filter(customer_id=customer.cust_id)
                    serializer_class = serializers_dict.get(model.__name__)
                    if serializer_class:
                        serializer = serializer_class(queryset, many=True)
                        data[model.__name__.lower()] = serializer.data

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class CustomerMsebView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    Gen_models='CustomerMseb'

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            auth_user = AuthUser.objects.filter(username=user.username).first()
            if not auth_user:
                return Response({"error": "User not found in AuthUser table."}, status=status.HTTP_404_NOT_FOUND)

            customer = Customer.objects.filter(comp_name=auth_user.username).first()
            if not customer:
                return Response({"error": "Customer profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

              # Fetch data from all models related to the customer
            data = {}

            for model in Gen_models:
                if hasattr(model, 'customer'):
                    queryset = model.objects.filter(comp_name=customer.comp_name)
                    serializer = CustomerMsebSerializer(queryset, many=True)
                    data['customermseb'] = serializer.data

            # return Response(data, status=status.HTTP_200_OK)
            return Response(data['customermseb'], status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CustomerGenerationMeterView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user
#             auth_user = AuthUser.objects.filter(id=user.id).first()
#             if not auth_user:
#                 return Response({"error": "User not found in AuthUser table."}, status=status.HTTP_404_NOT_FOUND)

#             customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
#             if not customer:
#                 return Response({"error": "Customer profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

#             queryset = CustomerGenerationmeter.objects.filter(customer_id=customer.cust_id)
#             serializer = CustomerGenerationMeterSerializer(queryset, many=True)

#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# import logging

# logger = logging.getLogger(__name__)

# class CustomerGenerationMeterView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             # Get the logged-in user
#             user = request.user
#             logger.info(f"Logged-in user: {user.id}")

#             # Find the corresponding AuthUser record
#             auth_user = AuthUser.objects.filter(id=user.id).first()
#             if not auth_user:
#                 logger.warning(f"AuthUser not found for user ID: {user.id}")
#                 return Response({"error": "User not found in AuthUser table."}, status=status.HTTP_404_NOT_FOUND)

#             logger.info(f"Found AuthUser: {auth_user.id}")

#             # Find the customer associated with this user
#             customer = Customer.objects.filter(new_customer_id=auth_user.id).first()
#             if not customer:
#                 logger.warning(f"Customer profile not found for AuthUser ID: {auth_user.id}")
#                 return Response({"error": "Customer profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

#             logger.info(f"Found Customer: {customer.cust_id}")

#             # Fetch all generation meters linked to this customer
#             queryset = CustomerGenerationmeter.objects.filter(customer_id=customer.cust_id)
#             if not queryset.exists():
#                 logger.warning(f"No generation meters found for Customer ID: {customer.cust_id}")
#                 return Response({"message": "No generation meters found for this user."}, status=status.HTTP_200_OK)

#             # Serialize the queryset
#             serializer = CustomerGenerationMeterSerializer(queryset, many=True)

#             logger.info(f"Returning {len(serializer.data)} generation meters for Customer ID: {customer.cust_id}")
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"An error occurred: {str(e)}", exc_info=True)
#             return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# from django.contrib.auth import authenticate
# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from django.apps import apps
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User
# from .models import *
# from .serializers import serializers_dict, CustomerSerializer

# # Dictionary to store dynamically generated viewsets
# viewsets_dict = {}

# # Fetch all models from this Django app
# all_models = list(apps.get_app_config('api').get_models())  # Replace 'api' with your actual app name

# for model in all_models:
#     serializer_class = serializers_dict.get(model.__name__)

#     if serializer_class:
#         viewset_class = type(
#             f"{model.__name__}ViewSet",
#             (viewsets.ModelViewSet,),
#             {
#                 "queryset": model.objects.all(),
#                 "serializer_class": serializer_class,
#                 "authentication_classes": [TokenAuthentication],
#                 "permission_classes": [IsAuthenticated],
#             }
#         )

#         viewsets_dict[model.__name__.lower()] = viewset_class


# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def secured_view(request):
#     return Response({"message": "This is a secured API"})


# # Custom Login View
# class CustomerLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         if not username or not password:
#             return Response(
#                 {"error": "Please provide both username and password."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = authenticate(username=username, password=password)

#         if user:
#             try:
#                 auth_user = AuthUser.objects.get(username=user.username)
#             except AuthUser.DoesNotExist:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             token, _ = Token.objects.get_or_create(user=user)

#             try:
#                 customer = Customer.objects.get(new_customer=auth_user)
#                 customer_serializer = CustomerSerializer(customer)
#             except Customer.DoesNotExist:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             return Response(
#                 {
#                     "token": token.key,
#                     "user": {
#                         "username": auth_user.username,
#                         "email": auth_user.email,
#                         "customer_details": customer_serializer.data,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"error": "Invalid username or password."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )


# class GetCustomerDetails(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user

#             auth_user = AuthUser.objects.filter(username=user.username).first()
#             if not auth_user:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer = Customer.objects.filter(new_customer=auth_user).first()
#             if not customer:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer_serializer = CustomerSerializer(customer)
#             return Response(
#                 {"customer_details": customer_serializer.data},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

# class CustomerDataView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user

#             # Fetch the AuthUser instance associated with the authenticated user
#             auth_user = AuthUser.objects.filter(username=user.username).first()
#             if not auth_user:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Fetch the Customer instance where `new_customer` is the authenticated user
#             customer = Customer.objects.filter(new_customer=auth_user).first()
#             if not customer:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Fetch data from all models related to the customer
#             data = {}
#             for model in all_models:
#                 if hasattr(model, 'customer'):
#                     queryset = model.objects.filter(customer=customer)
#                     serializer_class = serializers_dict.get(model.__name__)
#                     if serializer_class:
#                         serializer = serializer_class(queryset, many=True)
#                         data[model.__name__.lower()] = serializer.data

#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )



# from django.contrib.auth import authenticate
# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.decorators import api_view, authentication_classes, permission_classes
# from django.apps import apps
# from rest_framework.authtoken.models import Token
# from django.contrib.auth.models import User
# #from .models import Customer, AuthUser
# from .serializers import serializers_dict, CustomerSerializer, MSEBSerializer, CustomerGenerationMeterSerializer

# # from .serializers import serializers_dict, CustomerSerializer, CustomerGenerationMeterSerializer, CustomerMetersSerializer, CustomerInspectionDetailSerializer, MSEBSerializer
# # from api.serializers import CustomerGenerationMeterSerializer

# from .models import *
# # Dictionary to store dynamically generated viewsets
# viewsets_dict = {}

# # Fetch all models from this Django app
# all_models = list(apps.get_app_config('api').get_models())  # Replace 'api' with your actual app name

# for model in all_models:
#     serializer_class = serializers_dict.get(model.__name__)

#     if serializer_class:
#         viewset_class = type(
#             f"{model.__name__}ViewSet",
#             (viewsets.ModelViewSet,),
#             {
#                 "queryset": model.objects.all(),
#                 "serializer_class": serializer_class
#             }
#         )

#         viewsets_dict[model.__name__.lower()] = viewset_class


# @api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def secured_view(request):
#     return Response({"message": "This is a secured API"})


# # Custom Login View
# class CustomerLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         if not username or not password:
#             return Response(
#                 {"error": "Please provide both username and password."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = authenticate(username=username, password=password)

#         if user:
#             try:
#                 auth_user = AuthUser.objects.get(username=user.username)
#             except AuthUser.DoesNotExist:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             token, _ = Token.objects.get_or_create(user=user)

#             try:
#                 customer = Customer.objects.get(new_customer=auth_user)
#                 customer_serializer = CustomerSerializer(customer)
#             except Customer.DoesNotExist:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             return Response(
#                 {
#                     "token": token.key,
#                     "user": {
#                         "username": auth_user.username,
#                         "email": auth_user.email,
#                         "customer_details": customer_serializer.data,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"error": "Invalid username or password."},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )


# class GetCustomerDetails(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user

#             auth_user = AuthUser.objects.filter(username=user.username).first()
#             if not auth_user:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer = Customer.objects.filter(new_customer=auth_user).first()
#             if not customer:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             customer_serializer = CustomerSerializer(customer)
#             return Response(
#                 {"customer_details": customer_serializer.data},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )




# class MSEBView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user

#             auth_user = AuthUser.objects.filter(username=user.username).first()
#             if not auth_user:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             mseb = CustomerMseb.objects.filter(customer__new_customer=auth_user).first()

#             if not mseb:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             mseb_serializer = MSEBSerializer(mseb)
#             return Response(
#                 {"mseb_details": mseb_serializer.data},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

# class GenerationMeter(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             user = request.user

#             # Fetch the AuthUser instance associated with the authenticated user
#             auth_user = AuthUser.objects.filter(username=user.username).first()
#             if not auth_user:
#                 return Response(
#                     {"error": "User not found in AuthUser table."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Fetch the Customer instance associated with the AuthUser
#             customer = Customer.objects.filter(new_customer=auth_user).first()
#             if not customer:
#                 return Response(
#                     {"error": "Customer profile not found for this user."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Fetch the Generation Meter records associated with the Customer
#             meters = CustomerGenerationmeter.objects.filter(customer=customer)
#             if not meters:
#                 return Response(
#                     {"error": "No generation meter records found for this customer."},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Serialize the data
#             GenerationMeter_serializer = CustomerGenerationMeterSerializer(meters, many=True)
#             return Response(
#                 {"GenerationMeter_details": GenerationMeter_serializer.data},
#                 status=status.HTTP_200_OK,
#             )

#         except Exception as e:
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )



# # class GenerationMeter(APIView):
# #     authentication_classes = [TokenAuthentication]
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         try:
# #             user = request.user

# #             auth_user = AuthUser.objects.filter(id=user.id).first()
# #             if not auth_user:
# #                 return Response(
# #                     {"error": "User not found in AuthUser table."},
# #                     status=status.HTTP_404_NOT_FOUND,
# #                 )

# #             meter = CustomerGenerationmeter.objects.filter(customer__new_customer=auth_user).first()


# #             if not meter:
# #                 return Response(
# #                     {"error": "Customer profile not found for this user."},
# #                     status=status.HTTP_404_NOT_FOUND,
# #                 )

# #             GenerationMeter_serializer = CustomerGenerationMeterSerializer(meter)
# #             return Response(
# #                 {"GenerationMeter_details": GenerationMeter_serializer.data},
# #                 status=status.HTTP_200_OK,
# #             )

# #         except Exception as e:
# #             return Response(
# #                 {"error": f"An unexpected error occurred: {str(e)}"},
# #                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             )




# # # Explicitly define viewsets for required models
# # class CustomerGenerationMeterViewSet(viewsets.ModelViewSet):
# #     queryset = CustomerGenerationMeter.objects.all()
# #     serializer_class = CustomerGenerationMeterSerializer
# #     authentication_classes = [TokenAuthentication]
# #     permission_classes = [IsAuthenticated]

# # class CustomerMetersViewSet(viewsets.ModelViewSet):
# #     queryset = CustomerMeters.objects.all()
# #     serializer_class = CustomerMetersSerializer
# #     authentication_classes = [TokenAuthentication]
# #     permission_classes = [IsAuthenticated]

# # class CustomerInspectionDetailViewSet(viewsets.ModelViewSet):
# #     queryset = CustomerInspectionDetail.objects.all()
# #     serializer_class = CustomerInspectionDetailSerializer
# #     authentication_classes = [TokenAuthentication]
# #     permission_classes = [IsAuthenticated]

# # class MSEBView(viewsets.ModelViewSet):
# #     queryset = MSEB.objects.all()
# #     serializer_class = MSEBSerializer
# #     authentication_classes = [TokenAuthentication]
# #     permission_classes = [IsAuthenticated]