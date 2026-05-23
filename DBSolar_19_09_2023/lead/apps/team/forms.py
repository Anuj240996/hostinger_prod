# from django import forms
# from django.contrib.auth.models import User
# from apps.core.models import UserProfile
# from apps.control_panel.models import Role
#
# class UserCreationForm(forms.Form):
#     # Basic Info
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     email = forms.EmailField(required=True)
#     phone = forms.CharField(max_length=20, required=False)
#     title = forms.CharField(max_length=100, required=False)
#     department = forms.CharField(max_length=100, required=False)
#
#     # Role & Access
#     role = forms.ModelChoiceField(
#         queryset=Role.objects.none(),
#         required=True,
#         empty_label="Select a role"
#     )
#     is_active = forms.BooleanField(initial=True, required=False)
#
#     # Account Settings
#     password_option = forms.ChoiceField(
#         choices=[
#             ('auto', 'Auto-generate password'),
#             ('manual', 'Set password manually')
#         ],
#         widget=forms.RadioSelect,
#         initial='auto',
#         required=True
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput,
#         required=False,
#         help_text="Leave blank to auto-generate"
#     )
#     confirm_password = forms.CharField(
#         widget=forms.PasswordInput,
#         required=False
#     )
#     send_welcome_email = forms.BooleanField(initial=True, required=False)
#
#     def __init__(self, organization, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.organization = organization
#         self.fields['role'].queryset = Role.objects.filter(organization=organization)
#
#     def clean_email(self):
#         email = self.cleaned_data['email']
#         # Check if a user with this email already exists in the same organization
#         # We need to look up via profile
#         if UserProfile.objects.filter(organization=self.organization, user__email=email).exists():
#             raise forms.ValidationError("A user with this email already exists in your organization.")
#         return email
#
#     def clean(self):
#         cleaned_data = super().clean()
#         password_option = cleaned_data.get('password_option')
#         password = cleaned_data.get('password')
#         confirm = cleaned_data.get('confirm_password')
#
#         if password_option == 'manual':
#             if not password:
#                 self.add_error('password', 'Password is required when manual option is selected.')
#             elif password != confirm:
#                 self.add_error('confirm_password', 'Passwords do not match.')
#         return cleaned_data


from django import forms
from django.contrib.auth.models import User
from apps.core.models import UserProfile
from apps.control_panel.models import Role, UserRole


class UserCreationForm(forms.Form):
    # Basic Info
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    title = forms.CharField(max_length=100, required=False)
    department = forms.CharField(max_length=100, required=False)

    # Role & Access
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        required=True,
        empty_label="Select a role",
        label="Role",
        help_text="Select a role for the user. Each role has specific permissions."
    )
    is_active = forms.BooleanField(initial=True, required=False)

    # Account Settings
    password_option = forms.ChoiceField(
        choices=[
            ('auto', 'Auto-generate password'),
            ('manual', 'Set password manually')
        ],
        widget=forms.RadioSelect,
        initial='auto',
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to auto-generate"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )
    send_welcome_email = forms.BooleanField(initial=True, required=False)

    def __init__(self, organization, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        # Filter roles to the current organization
        roles_qs = Role.objects.filter(organization=organization)
        self.fields['role'].queryset = roles_qs
        # Customize the display of each role
        self.fields['role'].label_from_instance = self.role_label

    def role_label(self, role):
        """Return a label showing role name and permission count."""
        perm_count = role.permissions.count()
        return f"{role.name} ({perm_count} permission{'s' if perm_count != 1 else ''})"

    def clean_email(self):
        email = self.cleaned_data['email']
        if UserProfile.objects.filter(organization=self.organization, user__email=email).exists():
            raise forms.ValidationError("A user with this email already exists in your organization.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password_option = cleaned_data.get('password_option')
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password_option == 'manual':
            if not password:
                self.add_error('password', 'Password is required when manual option is selected.')
            elif password != confirm:
                self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


from django import forms
from django.contrib.auth.models import User
from apps.core.models import UserProfile
from apps.control_panel.models import Role

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, disabled=True, help_text="Email cannot be changed.")
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        required=True,
        empty_label="Select a role"
    )
    is_active = forms.BooleanField(required=False, initial=True)

    class Meta:
        model = UserProfile
        fields = ['phone', 'title', 'department']

    def __init__(self, organization, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            # Get current role
            current_role = self.instance.user.userrole_set.first()
            if current_role:
                self.fields['role'].initial = current_role.role
        self.fields['role'].queryset = Role.objects.filter(organization=organization)

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Update user fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            # email is not updated because disabled
            user.is_active = self.cleaned_data['is_active']
            user.save()
            # Update role
            new_role = self.cleaned_data['role']
            UserRole.objects.update_or_create(
                user=user,
                organization=self.organization,
                defaults={'role': new_role}
            )
        return profile