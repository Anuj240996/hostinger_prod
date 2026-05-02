from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, SubCategory, Product, Brand, Unit, Supplier


class SafeCategoryModelChoiceField(forms.ModelChoiceField):
    """
    Avoid MultipleObjectsReturned when the DB has duplicate Category rows for the same
    logical key (legacy data). Prefer lowest id.
    """

    def to_python(self, value):
        if value in self.empty_values:
            return None
        key = self.to_field_name or "pk"
        try:
            qs = self.queryset.filter(**{key: value})
        except (ValueError, TypeError):
            raise forms.ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        cnt = qs.count()
        if cnt == 0:
            raise forms.ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        if cnt > 1:
            return qs.order_by("id").first()
        return qs.first()


class CategoryForm(forms.ModelForm):
    """
    Model has null=True on name/short_name but not blank=True, so ModelForm would
    incorrectly require short_name. We require name only; short_name is optional.
    Empty short_name is stored as NULL so unique=True does not clash on ''.
    """

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
                'placeholder': 'Enter Short Name (optional)',
            }),
             'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input d-inline-block',  # Updated to include d-inline-block
                'style': 'margin-left: 10px; width:20px; height:20px;',  # Add margin-left to create space
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['short_name'].required = False
        # Unchecked checkbox is omitted from POST; must not be "required"
        self.fields['status'].required = False

    def clean_name(self):
        data = (self.cleaned_data.get('name') or '').strip()
        if not data:
            raise forms.ValidationError('Category name is required.')
        return data

    def clean_short_name(self):
        data = self.cleaned_data.get('short_name')
        if data is None:
            return None
        data = data.strip()
        return data or None

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"] = SafeCategoryModelChoiceField(
            queryset=Category.objects.all().order_by("name", "id"),
            required=True,
            widget=forms.Select(
                attrs={"class": "form-control item1", "style": "color: black;"}
            ),
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"] = SafeCategoryModelChoiceField(
            queryset=Category.objects.all().order_by("name", "id"),
            required=True,
            widget=forms.Select(
                attrs={"class": "form-control item1", "style": "color: black;"}
            ),
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"] = SafeCategoryModelChoiceField(
            queryset=Category.objects.all().order_by("name", "id"),
            required=True,
            widget=forms.Select(
                attrs={
                    "class": "form-control item1",
                    "placeholder": "Select Category",
                }
            ),
        )

