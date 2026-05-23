from django import forms
from django.contrib.auth.models import User
from apps.core.models import Organization, UserProfile
from .models import Role, Permission, Feature, OrganizationFeature, SubscriptionPlan, OrganizationSubscription
from django import forms
from apps.core.models import Organization

# ---------- Organization ----------
class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
        }

# ---------- User ----------
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        # Exclude password – handled separately

# We also need to edit the UserProfile (organization, phone, etc.)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['organization', 'phone', 'is_tenant_admin']

# ---------- Role & Permission ----------
# class RoleForm(forms.ModelForm):
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )
#
#     class Meta:
#         model = Role
#         fields = ['name', 'organization', 'permissions']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Order permissions by app_label and codename
#         self.fields['permissions'].queryset = Permission.objects.all().order_by('content_type__app_label', 'codename')
class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Role
        fields = ['name', 'organization', 'permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order permissions by app_label and codename (since content_type is not available)
        self.fields['permissions'].queryset = Permission.objects.all().order_by('app_label', 'codename')
# ---------- Feature ----------
class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = '__all__'

# ---------- OrganizationFeature ----------
class OrganizationFeatureForm(forms.ModelForm):
    class Meta:
        model = OrganizationFeature
        fields = '__all__'

# ---------- SubscriptionPlan ----------
class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

# ---------- OrganizationSubscription ----------
class OrganizationSubscriptionForm(forms.ModelForm):
    class Meta:
        model = OrganizationSubscription
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class OrganizationLimitsForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['max_users', 'max_storage_mb', 'api_rate_limit', 'leads_limit', 'quotations_limit']