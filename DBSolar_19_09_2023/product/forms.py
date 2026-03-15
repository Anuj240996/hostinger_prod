from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from .models import Category, SubCategory, Product, Brand, Unit, Supplier

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'short_name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Category Name',
                'style': 'color: black;',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Short Name',
            }),
             'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'short_name', 'status']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control item1',
                'style': 'color: black;',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter SubCategory Name',
                'style': 'color: black;',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Short Name',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }



# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['category', 'subcategory', 'name', 'prod_description', 'stock_alert', 'status', 'purchase', 'sales']
#         widgets = {
#             'category': forms.Select(attrs={
#                 'class': 'form-control item1',
#                 'style': 'color: black;',
#             }),
#             'subcategory': forms.Select(attrs={
#                 'class': 'form-control item1',
#                 'style': 'color: black;',
#             }),
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control item1',
#                 'placeholder': 'Enter Category Name',
#                 'style': 'color: black;',
#             }),
#             'prod_description': forms.Textarea(attrs={
#                 'class': 'form-control item1',
#                 'placeholder': 'Enter Short Name',
#             }),
#             'stock_alert': forms.NumberInput(attrs={  # Changed to NumberInput
#                 'class': 'form-control item1',
#                 'placeholder': 'Enter Stock Alert',
#                 'style': 'color: black;',
#             }),
#             'purchase': forms.Select(attrs={
#                 'class': 'form-control item1',
#                 'placeholder': 'Enter Purchase Type',
#             }),
#             'sales': forms.Select(attrs={
#                 'class': 'form-control item1',
#                 'placeholder': 'Enter Sales Type',
#             }),
#             'status': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input',
#                 'style': 'width:20px; height:20px;',
#             }),
#         }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'subcategory', 'name', 'prod_description', 'stock_alert', 'status', 'purchase', 'sales']

        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control item1',
                'style': 'color: black;',
            }),
            'subcategory': forms.Select(attrs={
                'class': 'form-control item1',
                'style': 'color: black;',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Product Name',
                'style': 'color: black;',
            }),
            'prod_description': forms.Textarea(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Short Name',
            }),
            'stock_alert': forms.NumberInput(attrs={  # Changed to NumberInput
                'class': 'form-control item1',
                'placeholder': 'Enter Stock Alert',
                'style': 'color: black;',
            }),
            'purchase': forms.Select(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Purchase Unit',
            }),
            'sales': forms.Select(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Sales Unit',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Brand Name',
                'style': 'color: black;',
            }),

            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'short_name']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Unit Name',
                'style': 'color: black;',
            }),
            'short_name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Short Name',
            }),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['supplier_name', 'contact_person', 'contact_email', 'contact_phone', 'category', 'address', 'city', 'state', 'post_code', 'gst_no', 'status']
        widgets = {
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Supplier Name',
                'style': 'color: black;',
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Contact Person Name',
            }),
            'contact_email': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Contact Email',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Contact Phone No.',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control item1',
                'placeholder': 'Select Category',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter City',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter State',
            }),
            'post_code': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter Post Code',
            }),
            'gst_no': forms.TextInput(attrs={
                'class': 'form-control item1',
                'placeholder': 'Enter GST No.',
            }),

            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }

