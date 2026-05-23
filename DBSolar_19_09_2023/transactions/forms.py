from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory, modelformset_factory
from django.forms.models import ModelChoiceField

from customer.models import Customer
from product.models import Category, Unit
from .models import (
    Supplier,
    Vendor,
    PurchaseBill,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails, FinalSale
)
from inventory.models import Stock


class SafeCategoryModelChoiceField(ModelChoiceField):
    """
    Like ModelChoiceField but resolves with filter().first() so duplicate Category
    rows (legacy DB) do not raise MultipleObjectsReturned from queryset.get().
    """

    def to_python(self, value):
        if value in self.empty_values:
            return None
        self.validate_no_null_characters(value)
        try:
            key = self.to_field_name or "pk"
            if isinstance(value, self.queryset.model):
                return value
            resolved = self.queryset.filter(**{key: value}).order_by("id").first()
            if resolved is None:
                raise self.queryset.model.DoesNotExist
            return resolved
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )


# form used to select a supplier
class SelectSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(status=True, is_deleted=False)
        self.fields['supplier'].widget.attrs.update({'class': 'textinput form-control'})
    class Meta:
        model = PurchaseBill
        fields = ['supplier']

# form used to render a single stock item form
class PurchaseItemForm(forms.ModelForm):
    purchase = forms.ModelChoiceField(queryset=Unit.objects.all(), required=True)  #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.for_forms_dropdown()
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update({'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})
        self.fields['purchase'].widget = forms.HiddenInput()
    class Meta:
        model = PurchaseItem
        fields = ['stock', 'purchase', 'quantity', 'perprice']



# formset used to render multiple 'PurchaseItemForm'
# PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)
PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)
# PurchaseItemFormset = modelformset_factory(PurchaseItem, form=PurchaseItemForm, extra=1)





# form used to accept the other details for purchase bill
class PurchaseDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaseBillDetails
        fields = ['eway','veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']


# form used for supplier
class SupplierForm(forms.ModelForm):
    category = SafeCategoryModelChoiceField(
        queryset=Category.objects.all().order_by("name", "id"),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'pattern' : '[a-zA-Z\s]{1,50}', 'title' : 'Alphabets and Spaces only'})
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[a-zA-Z\s&]{1,50}', 'title': 'Alphabets, Spaces, and & only'})
        self.fields['phone'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{10}', 'title' : 'Numbers only'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15', 'pattern' : '[A-Z0-9]{15}', 'title' : 'GSTIN Format Required'})
        self.fields['contact_person'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['city'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['state'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['post_code'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['status'].widget.attrs.update({'class': 'checkbox form-control'})
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'address', 'email', 'category', 'address', 'city', 'state', 'post_code', 'gstin', 'status']
        widgets = {
            'address' : forms.Textarea(
                attrs = {
                    'class' : 'textinput form-control',
                    'rows'  : '4',
                    'placeholder': 'Enter Address',
                }),
            #
            # 'name': forms.TextInput(attrs={
            #     'class' : 'textinput form-control',
            #     'placeholder': 'Enter Supplier Name',
            #     'style': 'color: black;',
            # }),
            'name': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter Supplier Name',
                'style': 'color: black;',
                'pattern': '[a-zA-Z\s&]{1,50}',  # Ensure the pattern is also applied here
                'title': 'Alphabets, Spaces, and & only'
            }),
            'contact_person': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter Contact Person Name',
            }),
            'email': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter Contact Email',
            }),
            'phone': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter Contact Phone No.',
            }),
            'category': forms.Select(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Select Category',
            }),

            'city': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter City',
            }),
            'state': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter State',
            }),
            'post_code': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter Post Code',
            }),
            'gst_no': forms.TextInput(attrs={
                'class' : 'textinput form-control',
                'placeholder': 'Enter GST No.',
            }),

            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }


#
# # form used for supplier
# class VendorForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'pattern' : '[a-zA-Z\s]{1,50}', 'title' : 'Alphabets and Spaces only'})
#         self.fields['phone'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{10}', 'title' : 'Numbers only'})
#         self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['gstin'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15', 'pattern' : '[A-Z0-9]{15}', 'title' : 'GSTIN Format Required'})
#         self.fields['contact_person'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['city'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['state'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['post_code'].widget.attrs.update({'class': 'textinput form-control'})
#         self.fields['status'].widget.attrs.update({'class': 'checkbox form-control'})
#     class Meta:
#         model = Vendor
#         fields = ['name', 'contact_person', 'phone', 'address', 'email', 'category', 'address', 'city', 'state', 'post_code', 'gstin', 'status']
#         widgets = {
#             'address' : forms.Textarea(
#                 attrs = {
#                     'class' : 'textinput form-control',
#                     'rows'  : '4',
#                     'placeholder': 'Enter Address',
#                 }),
#
#             'name': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter Vendor Name',
#                 'style': 'color: black;',
#             }),
#             'contact_person': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter Contact Person Name',
#             }),
#             'email': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter Contact Email',
#             }),
#             'phone': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter Contact Phone No.',
#             }),
#             'category': forms.Select(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Select Category',
#             }),
#
#             'city': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter City',
#             }),
#             'state': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter State',
#             }),
#             'post_code': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter Post Code',
#             }),
#             'gst_no': forms.TextInput(attrs={
#                 'class' : 'textinput form-control',
#                 'placeholder': 'Enter GST No.',
#             }),
#
#             'status': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
#                 'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
#             }),
#         }

class VendorForm(forms.ModelForm):
    category = SafeCategoryModelChoiceField(
        queryset=Category.objects.all().order_by("name", "id"),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'pattern': '[a-zA-Z\s]{1,50}', 'title': 'Alphabets and Spaces only'})
        self.fields['phone'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern': '[0-9]{10}', 'title': 'Numbers only'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].required = False  # Remove required attribute
        self.fields['gstin'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15', 'pattern': '[A-Z0-9]{15}', 'title': 'GSTIN Format Required'})
        self.fields['contact_person'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['city'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['state'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['post_code'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['status'].widget.attrs.update({'class': 'checkbox form-control'})

    class Meta:
        model = Vendor
        fields = ['name', 'contact_person', 'phone', 'address', 'email', 'category', 'address', 'city', 'state', 'post_code', 'gstin', 'status']
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'textinput form-control',
                'rows': '4',
                'placeholder': 'Enter Address',
            }),
            'name': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter Vendor Name',
                'style': 'color: black;',
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter Contact Person Name',
            }),
            'email': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter Contact Email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter Contact Phone No.',
            }),
            'category': forms.Select(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Select Category',
            }),
            'city': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter City',
            }),
            'state': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter State',
            }),
            'post_code': forms.TextInput(attrs={
                'class': 'textinput form-control',
                'placeholder': 'Enter Post Code',
            }),
            'gstin': forms.TextInput(attrs={  # Ensure correct field name is used
                'class': 'textinput form-control',
                'placeholder': 'Enter GST No. (Optional)',
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',
                'style': 'margin-left: 10px; width:20px; height:20px;',
            }),
        }

# form used to get customer details
class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'pattern' : '[a-zA-Z\s]{1,50}', 'title' : 'Alphabets and Spaces only', 'required': 'true'})
        self.fields['phone'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern' : '[0-9]{10}', 'title' : 'Numbers only', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '15', 'pattern' : '[A-Z0-9]{15}', 'title' : 'GSTIN Format Required'})
    class Meta:
        model = SaleBill
        fields = ['name', 'phone', 'address', 'email', 'gstin']
        widgets = {
            'address' : forms.Textarea(
                attrs = {
                    'class' : 'textinput form-control',
                    'rows'  : '4'
                }
            )
        }



# # form used to select a supplier
# class SelectSaleForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['Cust_id'].queryset = Customer.objects.all()
#         self.fields['Cust_id'].widget.attrs.update({'class': 'textinput form-control'})
#     class Meta:
#         model = Customer
#         fields = ['Cust_type']

# form used to select a supplier
class SelectSaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Cust_id'].queryset = Customer.objects.all()
        self.fields['Cust_id'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = SaleBill
        fields = ['Cust_id']

# class SelectSaleForm(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['Cust_type']

# form used to render a single stock item form
class SaleItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.for_forms_dropdown()
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        # self.fields['perprice'].widget.attrs.update({'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})
    class Meta:
        model = SaleItem
        fields = ['stock', 'quantity']
        # fields = ['stock', 'quantity', 'perprice']

# formset used to render multiple 'SaleItemForm'
SaleItemFormset = formset_factory(SaleItemForm, extra=1)




# form used to render a single stock item form
class SaleItemForm_bill(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.for_forms_dropdown()
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update({'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})
    class Meta:
        model = SaleItem
        # fields = ['stock', 'quantity']
        fields = ['stock', 'quantity', 'perprice']

# formset used to render multiple 'SaleItemForm'
SaleItemFormset_bill = formset_factory(SaleItemForm, extra=1)




# form used to accept the other details for sales bill
class SaleDetailsForm(forms.ModelForm):
    class Meta:
        model = SaleBillDetails
        fields = ['eway','veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']


class SerialSearchForm(forms.Form):
    serial_no = forms.CharField(label='Enter Serial No', max_length=50)
