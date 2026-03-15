# from rest_framework import serializers
# from django.apps import apps
# from .models import Customer, CustomerMseb

# # Dictionary to store dynamically generated serializers
# serializers_dict = {}

# # Fetch all models from this Django app
# all_models = apps.get_app_config('api').get_models()  # Replace 'api' with your actual app name

# for model in all_models:
#     class Meta:
#         model = model
#         fields = '__all__'

#     serializer_class = type(
#         f"{model.__name__}Serializer",
#         (serializers.ModelSerializer,),
#         {"Meta": Meta}
#     )

#     serializers_dict[model.__name__] = serializer_class

# # Dedicated serializer for Customer
# class CustomerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Customer
#         fields = '__all__'

# class CustomerMsebSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerMseb  # Make sure this is the correct model
#         fields = "__all__"
# class CustomerMsebSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerMseb  # Make sure this is the correct model
#         fields = "__all__"


from rest_framework import serializers
from django.apps import apps
from .models import Customer, CustomerMseb, CustomerGenerationmeter  # Explicitly importing Customer
# from .models import Customer, CustomerGenerationMeter, CustomerMeters, CustomerInspectionDetail, MSEB


# Dictionary to store dynamically generated serializers
serializers_dict = {}

# Fetch all models from this Django app
all_models = apps.get_app_config('api').get_models()  # Replace 'api' with your actual app name

for model in all_models:
    class Meta:
        model = model
        fields = '__all__'

    serializer_class = type(
        f"{model.__name__}Serializer",
        (serializers.ModelSerializer,),
        {"Meta": Meta}
    )

    serializers_dict[model.__name__] = serializer_class


# Dedicated serializer for Customer
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


# class CustomerGenerationMeterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerGenerationmeter
#         fields = '__all__'

# # class CustomerMetersSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = CustomerMeters
# #         fields = '__all__'

# # class CustomerInspectionDetailSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = CustomerInspectionDetail
# #         fields = '__all__'

# class MSEBSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerMseb
#         fields = '__all__'
