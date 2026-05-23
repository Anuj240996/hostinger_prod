import pytz
from django import forms
from django.contrib.auth.models import User
from .models import Organization
from .utils import generate_unique_subdomain

class Step1BusinessForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['legal_name', 'trade_name', 'business_type', 'industry',
                  'gst_number', 'pan_tax_id', 'registration_number']
        widgets = {
            'legal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter legal name'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Solar Energy'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 22AAAAA0000A1Z5'}),
            'pan_tax_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ABCDE1234F'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company registration'}),
        }

    # Add GST/PAN validation (optional, can be added later)


class Step2AddressForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
        }


class Step3ContactForm(forms.ModelForm):
    # Override timezone and currency fields with choices
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    currency = forms.ChoiceField(
        choices=[
            ('INR', 'INR - Indian Rupee'),
            ('USD', 'USD - US Dollar'),
            ('EUR', 'EUR - Euro'),
            ('GBP', 'GBP - British Pound'),
            ('AED', 'AED - UAE Dirham'),
            ('SAR', 'SAR - Saudi Riyal'),
            ('CAD', 'CAD - Canadian Dollar'),
            ('AUD', 'AUD - Australian Dollar'),
            ('JPY', 'JPY - Japanese Yen'),
            ('CNY', 'CNY - Chinese Yuan'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Organization
        fields = ['official_email', 'phone', 'alternate_phone', 'billing_email', 'website', 'timezone', 'currency']
        widgets = {
            'official_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'official@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'billing_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'billing@example.com'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }

    def clean_official_email(self):
        email = self.cleaned_data.get('official_email')
        if Organization.objects.filter(official_email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class Step4BrandingForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['logo', 'digital_signature', 'company_stamp', 'primary_color', 'secondary_color']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'digital_signature': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_stamp': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class Step5AdminForm(forms.Form):
    admin_full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'})
    )
    admin_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'admin@example.com'})
    )
    admin_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    def clean_admin_email(self):
        email = self.cleaned_data.get('admin_email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data