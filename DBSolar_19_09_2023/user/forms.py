# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User
# from .models import Profile

# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User



# class UserLoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super(UserLoginForm, self).__init__(*args, **kwargs)

#     username = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#       # "placeholder": "enter username"
#     }))

#     password = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#       #  "placeholder": "enter password"
#     }))


# # class CreateUserForm(UserCreationForm):
# #     username = forms.CharField(widget=forms.TextInput(attrs={
# #         "class": "input",
# #         "type": "text",
# #         "placeholder": "enter username"
# #     }))
# #
# #     first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={
# #         "class": "input",
# #         "type": "first_name",
# #         "placeholder": "enter first name"
# #     }))
# #
# #     last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={
# #         "class": "input",
# #         "type": "last_name",
# #         "placeholder": "enter last name"
# #     }))
# #      #email = forms.EmailField()
# #     email = forms.CharField(widget=forms.TextInput(attrs={
# #          "class": "input",
# #          "type": "email",
# #          "placeholder": "enter email-id"
# #      }))
# #
# #     password1 = forms.CharField(label='Password', widget=forms.TextInput(attrs={
# #         "class": "input",
# #         "type": "password",
# #         "placeholder": "enter password"
# #     }))
# #
# #     password2 = forms.CharField(label='Confirm Password (again)', widget=forms.TextInput(attrs={
# #         "class": "input",
# #         "type": "password",
# #         "placeholder": "re-enter password"
# #     }))
# #     is_active = forms.BooleanField(label='Active', initial=True, required=False, widget=forms.CheckboxInput(attrs={
# #         "class": "checkbox",
# #         "id": "is_active_checkbox",
# #     }))
# #     is_superuser = forms.BooleanField(label='Superuser', initial=False, required=False,
# #                                       widget=forms.CheckboxInput(attrs={
# #                                           "class": "checkbox",
# #                                           "id": "is_superuser_checkbox",
# #                                       }))
# #     is_staff = forms.BooleanField(label='Staff', initial=False, required=False, widget=forms.CheckboxInput(attrs={
# #         "class": "checkbox",
# #         "id": "is_staff_checkbox",
# #     }))
# #
# #
# #     is_active = forms.BooleanField(label='Consumer', initial=True, required=False)
# #     is_superuser = forms.BooleanField(label='Superuser', initial=False, required=False)
# #     is_staff = forms.BooleanField(label='Staff', initial=False, required=False)
# #
# #     # class Meta:
# #     #     model = User
# #     #     fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
# #     #     #labels = {'first_name': 'First Name', 'last_name': 'Last Name'}
# #     #     # fields = '__all__'
# #     #
# #
# #     class Meta(UserCreationForm.Meta):
# #         model = User
# #         fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_active', 'is_superuser',
# #                   'is_staff']
# #         labels = {'first_name': 'First Name', 'last_name': 'Last Name'}
# #

# # from crispy_forms.helper import FormHelper
# # from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
# # from django import forms
# # from django.contrib.auth.forms import UserCreationForm
# # from django.contrib.auth.models import User


# class CreateUserForm(UserCreationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#         "placeholder": "enter username"
#     }))

#     first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "first_name",
#         "placeholder": "Enter First Name"
#     }))

#     last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "last_name",
#         "placeholder": "Enter Last Name"
#     }))

#     email = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "email",
#         "placeholder": "Enter Email-id",
#     }), required=True)

#     password1 = forms.CharField(label='Password', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         "placeholder": "Enter Password"
#     }))

#     password2 = forms.CharField(label='Confirm Password (again)', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         "placeholder": "Re-Enter Password"
#     }))

#     is_active = forms.BooleanField(
#         label='Active',
#         initial=True,
#         required=False,
#         widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1'})
#     )
#     is_active = forms.BooleanField(
#         label='Active',
#         initial=True,
#         required=False,
#         widget=forms.CheckboxInput(
#             attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1', 'template': 'add.html'})
#     )


#     is_superuser = forms.BooleanField(
#         label='Administrator',
#         initial=False,
#         required=False,
#         widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1'})
#     )

#     is_staff = forms.BooleanField(
#         label='Staff',
#         initial=True,
#         required=False,
#         widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1', 'template': 'add.html'})
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_active', 'is_superuser', 'is_staff']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             Fieldset(
#                 'User Information',
#                 Row(
#                     Column('username', css_class='form-group col-md-6 mb-0'),
#                     Column('email', css_class='form-group col-md-6 mb-0'),
#                     css_class='form-row'
#                 ),
#                 Row(
#                     Column('first_name', css_class='form-group col-md-6 mb-0'),
#                     Column('last_name', css_class='form-group col-md-6 mb-0'),
#                     css_class='form-row'
#                 ),
#             ),
#             Fieldset(
#                 'Password Information',
#                 Row(
#                     Column('password1', css_class='form-group col-md-6 mb-0'),
#                     Column('password2', css_class='form-group col-md-6 mb-0'),
#                     css_class='form-row'
#                 ),
#             ),
#             Fieldset(
#                 'User Permissions',
#                 Row(
#                     Column('is_active', css_class='form-check col-md-4 mb-0'),
#                     Column('is_superuser', css_class='form-check col-md-4 mb-0'),
#                     Column('is_staff', css_class='form-check col-md-4 mb-0'),
#                     css_class='form-row'
#                 ),
#             ),
#             Submit('submit', 'Create Account', css_class='btn-primary')
#         )



# class UserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email']


# class ProfileUpdateForm(forms.ModelForm):
#     DOB = forms.DateField()
#     class Meta:
#         model = Profile
#         fields = ['phone', 'address', 'department', 'image', 'DOB']
# # forms.py
# from django import forms
# from .models import User, Profile

# # class PDFGenerationForm(forms.Form):
# #     user_fields = forms.MultipleChoiceField(
# #         choices=[(field.name, field.verbose_name) for field in User._meta.get_fields() if field.concrete],
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #     profile_fields = forms.MultipleChoiceField(
# #         choices=[(field.name, field.verbose_name) for field in Profile._meta.get_fields() if field.concrete],
# #         widget=forms.CheckboxSelectMultiple
# #     )

# from django import forms
# from django.contrib.auth.models import User
# from user.models import Profile
# from django.db import models

# from django import forms
# from django.contrib.auth.models import User
# from user.models import Profile
# from django.db.models.fields.related import ManyToOneRel, ManyToManyRel


# # class PDFGenerationForm(forms.Form):
# #     user_fields = forms.MultipleChoiceField(
# #         choices=[
# #             (field.name, field.verbose_name)
# #             for field in User._meta.get_fields()
# #             if not isinstance(field, (ManyToOneRel, ManyToManyRel))
# #                and field.name not in ['password', 'id', 'groups', 'user permissions', 'profile']
# #         ],
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #
# #     profile_fields = forms.MultipleChoiceField(
# #         choices=[
# #             (field.name, field.verbose_name)
# #             for field in Profile._meta.get_fields()
# #             if not isinstance(field, (ManyToOneRel, ManyToManyRel))
# #                and field.name not in ['customer', 'pg']
# #         ],
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #


#     #
#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#     #
#     #     # Customize the choices for the related fields
#     #     self.fields['user_fields'].choices += [
#     #         (f'profile.{field.name}', f'Profile - {field.verbose_name}')
#     #         for field in Profile._meta.get_fields()
#     #         if not isinstance(field, (ManyToOneRel, ManyToManyRel))
#     #            and field.name not in ['customer', 'pg']
#     #     ]
#     #
#     #     self.fields['profile_fields'].choices += [
#     #         (f'user.{field.name}', f'User - {field.verbose_name}')
#     #         for field in User._meta.get_fields()
#     #         if not isinstance(field, (ManyToOneRel, ManyToManyRel))
#     #            and field.name not in ['password', 'id', 'profile']
#     #     ]
#     #

# # class PDFGenerationForm(forms.Form):
# #     user_fields = forms.MultipleChoiceField(
# #         choices=[
# #             (field.name, field.verbose_name)
# #             for field in User._meta.get_fields()
# #             if field.name not in ['password', 'id', 'groups', 'user_permissions', 'profile']
# #                and not isinstance(field, ManyToOneRel)
# #         ],
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #
# #     profile_fields = forms.MultipleChoiceField(
# #         choices=[
# #             (field.name, field.verbose_name)
# #             for field in Profile._meta.get_fields()
# #             if field.name not in ['customer', 'pg']
# #         ],
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #
# #     def clean(self):
# #         cleaned_data = super().clean()
# #         user_fields = cleaned_data.get('user_fields', [])
# #         profile_fields = cleaned_data.get('profile_fields', [])
# #
# #         if not user_fields and not profile_fields:
# #             raise forms.ValidationError("At least one field from each table must be selected.")
# #
# #         return cleaned_data

# class FullNameField(forms.CharField):
#     def clean(self, value):
#         # Split the full name into first_name and last_name
#         first_name, last_name = value.split(' ', 1)
#         return {
#             'first_name': first_name,
#             'last_name': last_name,
#         }



# class PDFGenerationForm(forms.Form):
#     # user_fields = forms.MultipleChoiceField(
#     #     choices=[
#     #         (field.name, field.verbose_name)
#     #         for field in User._meta.get_fields()
#     #         if field.name not in ['password', 'id', 'groups', 'user_permissions', 'profile']
#     #            and not isinstance(field, ManyToOneRel)
#     #     ],
#     #     widget=forms.CheckboxSelectMultiple
#     # )
#     #
#     # full_name = FullNameField()  # Add the custom full_name field

#     # Create the choices list without 'first_name' and 'last_name'
#     user_choices = [
#         (field.name, field.verbose_name)
#         for field in User._meta.get_fields()
#         if field.name not in ['password', 'id', 'groups', 'user_permissions', 'profile', 'first_name', 'last_name', 'last_login',
#                               'is_superuser', 'is_active', 'is_staff','date_joined', 'username',
#                               'email']
#           and not isinstance(field, ManyToOneRel)
#     ]

#     # Add 'full_name' as a choice
#     user_choices.append(('username', 'Username'))
#     user_choices.append(('full_name', 'Full Name'))
#     user_choices.append(('email', 'Official Email'))

#     initial = ['first_name', 'username']

#     user_fields = forms.MultipleChoiceField(
#         choices=user_choices,
#         widget=forms.CheckboxSelectMultiple,
#         initial=initial  # Set 'Full Name' as initially selected
#     )


#     # user_fields = forms.MultipleChoiceField(
#     #     choices=user_choices,
#     #     widget=forms.CheckboxSelectMultiple
#     # )


#     # profile_fields = forms.MultipleChoiceField(
#     profile_choices = [
#         (field.name, field.verbose_name)
#         for field in Profile._meta.get_fields()
#         if field.name not in ['customer', 'pg', 'id', 'address', 'DOB', 'phone', 'department', 'designation', 'bg', 'city',
#                               'taluka', 'district', 'institution', 'yop', 'specili', 'last_updated_by', 'phone', 'emraddress', 'email',
#                               'image', 'workphone', 'name', 'phone']
#     ]

#     # Convert the tuple to a list
#     profile_choices = list(profile_choices)

#     # Add the additional choice
#     profile_choices.append(('customer_id', 'Emp ID'))
#     profile_choices.append(('address', 'Address'))
#     profile_choices.append(('DOB', 'Date Of Birth'))
#     profile_choices.append(('department', 'Department'))
#     profile_choices.append(('designation', 'Designation'))
#     profile_choices.append(('bg', 'Blood Group'))
#     profile_choices.append(('city', 'City'))
#     profile_choices.append(('taluka', 'Taluka'))
#     profile_choices.append(('district', 'District'))
#     profile_choices.append(('workphone', 'Official Contact No'))


#     initial = ['customer_id']
#     profile_fields = forms.MultipleChoiceField(
#         choices=profile_choices,
#         widget=forms.CheckboxSelectMultiple,
#         initial = initial  # Set 'Full Name' as initially selected

#     )

#     # full_name = forms.CharField(label='Full Name', required=False,
#     #                             widget=forms.TextInput(attrs={'readonly': 'readonly'}))

#     def clean(self):
#         cleaned_data = super().clean()
#         user_fields = cleaned_data.get('user_fields', [])
#         profile_fields = cleaned_data.get('profile_fields', [])

#         first_name = cleaned_data.get('first_name')
#         last_name = cleaned_data.get('last_name')

#         if first_name and last_name:
#             cleaned_data['full_name'] = f"{first_name} {last_name}"

#         total_selected_fields = len(user_fields) + len(profile_fields)
#         if total_selected_fields > 6:
#             raise forms.ValidationError("You can select a maximum of 6 fields.")

#         if not user_fields and not profile_fields and not cleaned_data.get('full_name'):
#             raise forms.ValidationError("At least one field from each table or Full Name must be selected.")

#         return cleaned_data


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User,Permission



class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        # "placeholder": "enter username"
    }))

    password = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "password",
        # "placeholder": "enter password"
    }))

    # password1 = forms.CharField(widget=forms.TextInput(attrs={
    #     "class": "input",
    #     "type": "password",
    #     # "placeholder": "enter password"
    # }))
    #
    #
    # email = forms.CharField(widget=forms.TextInput(attrs={
    #     "class": "input",
    #     "type": "email",
    #     # "placeholder": "enter password"
    # }))
    #
    # first_name = forms.CharField(widget=forms.TextInput(attrs={
    #     "class": "input",
    #     "type": "text",
    #     # "placeholder": "enter password"
    # }))
    #
    # last_name = forms.CharField(widget=forms.TextInput(attrs={
    #     "class": "input",
    #     "type": "text",
    #     # "placeholder": "enter password"
    # }))
    #
    # password2 = forms.CharField(widget=forms.TextInput(attrs={
    #     "class": "input",
    #     "type": "password",
    #     # "placeholder": "enter password"
    # }))
    #

#
# class UserForm(UserCreationForm):
#     def __init__(self, *args, **kwargs):
#         super(UserForm, self).__init__(*args, **kwargs)
#
#     username = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#         # "placeholder": "enter username"
#     }))
#
#     password1 = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         # "placeholder": "enter password"
#     }))
#
#
#     email = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "email",
#         # "placeholder": "enter password"
#     }))
#
#     first_name = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#         # "placeholder": "enter password"
#     }))
#
#     last_name = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#         # "placeholder": "enter password"
#     }))
#
#     password2 = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         # "placeholder": "enter password"
#     }))





# class CreateUserForm(UserCreationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "text",
#         "placeholder": "enter username"
#     }))
#
#     first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "first_name",
#         "placeholder": "enter first name"
#     }))
#
#     last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "last_name",
#         "placeholder": "enter last name"
#     }))
#      #email = forms.EmailField()
#     email = forms.CharField(widget=forms.TextInput(attrs={
#          "class": "input",
#          "type": "email",
#          "placeholder": "enter email-id"
#      }))
#
#     password1 = forms.CharField(label='Password', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         "placeholder": "enter password"
#     }))
#
#     password2 = forms.CharField(label='Confirm Password (again)', widget=forms.TextInput(attrs={
#         "class": "input",
#         "type": "password",
#         "placeholder": "re-enter password"
#     }))
#     is_active = forms.BooleanField(label='Active', initial=True, required=False, widget=forms.CheckboxInput(attrs={
#         "class": "checkbox",
#         "id": "is_active_checkbox",
#     }))
#     is_superuser = forms.BooleanField(label='Superuser', initial=False, required=False,
#                                       widget=forms.CheckboxInput(attrs={
#                                           "class": "checkbox",
#                                           "id": "is_superuser_checkbox",
#                                       }))
#     is_staff = forms.BooleanField(label='Staff', initial=False, required=False, widget=forms.CheckboxInput(attrs={
#         "class": "checkbox",
#         "id": "is_staff_checkbox",
#     }))
#
#
#     is_active = forms.BooleanField(label='Consumer', initial=True, required=False)
#     is_superuser = forms.BooleanField(label='Superuser', initial=False, required=False)
#     is_staff = forms.BooleanField(label='Staff', initial=False, required=False)
#
#     # class Meta:
#     #     model = User
#     #     fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
#     #     #labels = {'first_name': 'First Name', 'last_name': 'Last Name'}
#     #     # fields = '__all__'
#     #
#
#     class Meta(UserCreationForm.Meta):
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_active', 'is_superuser',
#                   'is_staff']
#         labels = {'first_name': 'First Name', 'last_name': 'Last Name'}
#

# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "placeholder": "Enter Username"
    }))

    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "pattern": "[A-Za-z]+",
        "placeholder": "Enter First Name"
    }))

    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "pattern": "[A-Za-z]+",
        "placeholder": "Enter Last Name"
    }))

    email = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "email",
        "placeholder": "Enter Email-id",
    }), required=True)

    password1 = forms.CharField(label='Password', widget=forms.TextInput(attrs={
        "class": "input",
        "type": "password",
        "placeholder": "Enter Password"
    }))

    password2 = forms.CharField(label='Confirm Password (again)', widget=forms.TextInput(attrs={
        "class": "input",
        "type": "password",
        "placeholder": "Re-Enter Password"
    }))

    is_active = forms.BooleanField(
        label='Active',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1'})
    )
    is_active = forms.BooleanField(
        label='Active',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1', 'template': 'add.html'})
    )


    is_superuser = forms.BooleanField(
        label='Administrator',
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1'})
    )

    is_staff = forms.BooleanField(
        label='Staff',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox', 'value': '1', 'template': 'add.html'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_active', 'is_superuser', 'is_staff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'User Information',
                Row(
                    Column('username', css_class='form-group col-md-6 mb-0'),
                    Column('email', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-0'),
                    Column('last_name', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Password Information',
                Row(
                    Column('password1', css_class='form-group col-md-6 mb-0'),
                    Column('password2', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'User Permissions',
                Row(
                    Column('is_active', css_class='form-check col-md-4 mb-0'),
                    Column('is_superuser', css_class='form-check col-md-4 mb-0'),
                    Column('is_staff', css_class='form-check col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Submit('submit', 'Create Account', css_class='btn-primary')
        )


from django import forms
from django.contrib.auth.models import User, Permission
from .models import Profile


# Existing code for PermissionForm
#
# class PermissionForm(forms.Form):
#     user = forms.ModelChoiceField(queryset=User.objects.all())
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#     )
#
#     # Add fields for user and permission selection
#     user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )
#
# class PasswordResetForm(forms.Form):
#     username = forms.CharField(max_length=150)
#     email = forms.EmailField()

from django import forms
from django.contrib.auth.models import User, Permission

# class PermissionForm(forms.Form):
#     user = forms.ModelChoiceField(queryset=User.objects.all())
#     permissions = forms.ModelMultipleChoiceField(
#         queryset=Permission.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#     )

class PermissionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        initial_user = kwargs.pop('initial_user', None)
        super().__init__(*args, **kwargs)
        if initial_user:
            self.fields['permissions'].initial = initial_user.user_permissions.all()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    DOB = forms.DateField()
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'department', 'image', 'DOB']
# forms.py
from django import forms
from .models import User, Profile

# class PDFGenerationForm(forms.Form):
#     user_fields = forms.MultipleChoiceField(
#         choices=[(field.name, field.verbose_name) for field in User._meta.get_fields() if field.concrete],
#         widget=forms.CheckboxSelectMultiple
#     )
#     profile_fields = forms.MultipleChoiceField(
#         choices=[(field.name, field.verbose_name) for field in Profile._meta.get_fields() if field.concrete],
#         widget=forms.CheckboxSelectMultiple
#     )

from django import forms
from django.contrib.auth.models import User
from user.models import Profile
from django.db import models

from django import forms
from django.contrib.auth.models import User
from user.models import Profile
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel


# class PDFGenerationForm(forms.Form):
#     user_fields = forms.MultipleChoiceField(
#         choices=[
#             (field.name, field.verbose_name)
#             for field in User._meta.get_fields()
#             if not isinstance(field, (ManyToOneRel, ManyToManyRel))
#                and field.name not in ['password', 'id', 'groups', 'user permissions', 'profile']
#         ],
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     profile_fields = forms.MultipleChoiceField(
#         choices=[
#             (field.name, field.verbose_name)
#             for field in Profile._meta.get_fields()
#             if not isinstance(field, (ManyToOneRel, ManyToManyRel))
#                and field.name not in ['customer', 'pg']
#         ],
#         widget=forms.CheckboxSelectMultiple
#     )
#


    #
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     # Customize the choices for the related fields
    #     self.fields['user_fields'].choices += [
    #         (f'profile.{field.name}', f'Profile - {field.verbose_name}')
    #         for field in Profile._meta.get_fields()
    #         if not isinstance(field, (ManyToOneRel, ManyToManyRel))
    #            and field.name not in ['customer', 'pg']
    #     ]
    #
    #     self.fields['profile_fields'].choices += [
    #         (f'user.{field.name}', f'User - {field.verbose_name}')
    #         for field in User._meta.get_fields()
    #         if not isinstance(field, (ManyToOneRel, ManyToManyRel))
    #            and field.name not in ['password', 'id', 'profile']
    #     ]
    #

# class PDFGenerationForm(forms.Form):
#     user_fields = forms.MultipleChoiceField(
#         choices=[
#             (field.name, field.verbose_name)
#             for field in User._meta.get_fields()
#             if field.name not in ['password', 'id', 'groups', 'user_permissions', 'profile']
#                and not isinstance(field, ManyToOneRel)
#         ],
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     profile_fields = forms.MultipleChoiceField(
#         choices=[
#             (field.name, field.verbose_name)
#             for field in Profile._meta.get_fields()
#             if field.name not in ['customer', 'pg']
#         ],
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     def clean(self):
#         cleaned_data = super().clean()
#         user_fields = cleaned_data.get('user_fields', [])
#         profile_fields = cleaned_data.get('profile_fields', [])
#
#         if not user_fields and not profile_fields:
#             raise forms.ValidationError("At least one field from each table must be selected.")
#
#         return cleaned_data

class FullNameField(forms.CharField):
    def clean(self, value):
        # Split the full name into first_name and last_name
        first_name, last_name = value.split(' ', 1)
        return {
            'first_name': first_name,
            'last_name': last_name,
        }



class PDFGenerationForm(forms.Form):
    # user_fields = forms.MultipleChoiceField(
    #     choices=[
    #         (field.name, field.verbose_name)
    #         for field in User._meta.get_fields()
    #         if field.name not in ['password', 'id', 'groups', 'user_permissions', 'profile']
    #            and not isinstance(field, ManyToOneRel)
    #     ],
    #     widget=forms.CheckboxSelectMultiple
    # )
    #
    # full_name = FullNameField()  # Add the custom full_name field

    # Create the choices list without 'first_name' and 'last_name'
    user_choices = [
        (field.name, getattr(field, 'verbose_name', field.name))
        for field in User._meta.get_fields()
        if field.name not in ['password', 'id', 'groups', 'user_permissions', 'profile', 'first_name', 'last_name', 'last_login',
                              'is_superuser', 'is_active', 'is_staff','date_joined', 'username',
                              'email']
           and not isinstance(field, ManyToOneRel)
           and hasattr(field, 'verbose_name')
    ]

    # Add 'full_name' as a choice
    user_choices.append(('username', 'Username'))
    user_choices.append(('full_name', 'Full Name'))
    user_choices.append(('email', 'Official Email'))

    initial = ['first_name', 'username']

    user_fields = forms.MultipleChoiceField(
        choices=user_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=initial  # Set 'Full Name' as initially selected
    )


    # user_fields = forms.MultipleChoiceField(
    #     choices=user_choices,
    #     widget=forms.CheckboxSelectMultiple
    # )


    # profile_fields = forms.MultipleChoiceField(
    profile_choices = [
        (field.name, field.verbose_name)
        for field in Profile._meta.get_fields()
        if field.name not in ['customer', 'pg', 'id', 'address', 'DOB', 'phone', 'department', 'designation', 'bg', 'city',
                              'taluka', 'district', 'institution', 'yop', 'specili', 'last_updated_by', 'phone', 'emraddress', 'email',
                              'image', 'workphone', 'name', 'phone']
    ]

    # Convert the tuple to a list
    profile_choices = list(profile_choices)

    # Add the additional choice
    profile_choices.append(('customer_id', 'Emp ID'))
    profile_choices.append(('address', 'Address'))
    profile_choices.append(('DOB', 'Date Of Birth'))
    profile_choices.append(('department', 'Department'))
    profile_choices.append(('designation', 'Designation'))
    profile_choices.append(('bg', 'Blood Group'))
    profile_choices.append(('city', 'City'))
    profile_choices.append(('taluka', 'Taluka'))
    profile_choices.append(('district', 'District'))
    profile_choices.append(('workphone', 'Official Contact No'))


    initial = ['customer_id']
    profile_fields = forms.MultipleChoiceField(
        choices=profile_choices,
        widget=forms.CheckboxSelectMultiple,
        initial = initial  # Set 'Full Name' as initially selected

    )

    # full_name = forms.CharField(label='Full Name', required=False,
    #                             widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    def clean(self):
        cleaned_data = super().clean()
        user_fields = cleaned_data.get('user_fields', [])
        profile_fields = cleaned_data.get('profile_fields', [])

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name and last_name:
            cleaned_data['full_name'] = f"{first_name} {last_name}"

        total_selected_fields = len(user_fields) + len(profile_fields)
        if total_selected_fields > 6:
            raise forms.ValidationError("You can select a maximum of 6 fields.")

        if not user_fields and not profile_fields and not cleaned_data.get('full_name'):
            raise forms.ValidationError("At least one field from each table or Full Name must be selected.")

        return cleaned_data

