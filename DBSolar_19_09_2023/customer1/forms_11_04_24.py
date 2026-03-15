from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from user.models import Profile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import customer_technical_Details, Meters
from .models import Customer


from django import forms
from django.contrib.auth.models import User
from user.models import Profile
from django.db import models

from django import forms
from django.contrib.auth.models import User
from user.models import Profile
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel



#
#
# class consumerGenerationForm(forms.Form):
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
#
#     # Create the choices list without 'first_name' and 'last_name'
#     customer_choices = [
#         (field.name, field.verbose_name)
#         for field in Customer._meta.get_fields()
#         if field.name not in ['email']
#            and not isinstance(field, ManyToOneRel)
#     ]
#
#     # Add 'full_name' as a choice
#     #customer_choices.append(('username', 'Username'))
#     customer_choices.append(('full_name', 'Full Name'))
#     customer_choices.append(('email', 'Official Email'))
#
#     initial = ['first_name', 'username']
#
#     customer_fields = forms.MultipleChoiceField(
#         choices=customer_choices,
#         widget=forms.CheckboxSelectMultiple,
#         initial=initial  # Set 'Full Name' as initially selected
#     )
#
#
#     # user_fields = forms.MultipleChoiceField(
#     #     choices=user_choices,
#     #     widget=forms.CheckboxSelectMultiple
#     # )
#
#
#     # # profile_fields = forms.MultipleChoiceField(
#     # profile_choices = [
#     #     (field.name, field.verbose_name)
#     #     for field in Profile._meta.get_fields()
#     #     if field.name not in ['customer', 'pg', 'id', 'address', 'DOB', 'phone', 'department', 'designation', 'bg', 'city',
#     #                           'taluka', 'district', 'institution', 'yop', 'specili', 'last_updated_by', 'phone', 'emraddress', 'email',
#     #                           'image', 'workphone', 'name', 'phone']
#     # ]
#
#
#     def clean(self):
#         cleaned_data = super().clean()
#         customer_fields = cleaned_data.get('customer_fields', [])
#
#
#         first_name = cleaned_data.get('first_name')
#         last_name = cleaned_data.get('last_name')
#
#         if first_name and last_name:
#             cleaned_data['full_name'] = f"{first_name} {last_name}"
#
#         total_selected_fields = len(customer_fields)
#         if total_selected_fields > 6:
#             raise forms.ValidationError("You can select a maximum of 6 fields.")
#
#         if not customer_fields and not cleaned_data.get('full_name'):
#             raise forms.ValidationError("At least one field from each table or Full Name must be selected.")
#
#         return cleaned_data
#



# forms.py

from django import forms
from .models import Customer

class consumerGenerationForm(forms.Form):
    # Create the choices list without 'first_name' and 'last_name'
    customer_choices = [
        (field.name, field.verbose_name)
        for field in Customer._meta.get_fields()
        if field.name not in ['email']
           and not isinstance(field, ManyToOneRel)
    ]

    # Add 'full_name' as a choice
    customer_choices.append(('full_name', 'Full Name'))
    customer_choices.append(('email', 'Official Email'))

    initial = ['first_name', 'username']

    customer_fields = forms.MultipleChoiceField(
        choices=customer_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=initial  # Set 'Full Name' as initially selected
    )

    userType = forms.ChoiceField(
        choices=(
            ('all', 'All Consumer Types'),
            ('Residential', 'Residential'),
            ('Commersial', 'Commercial'),
            ('Industrial', 'Industrial'),
            ('Goverment', 'Government'),
        ),
        required=False,  # Not required, as it's used for filtering
        widget=forms.RadioSelect,
        initial='all'  # Set the default option
    )

    def clean(self):
        cleaned_data = super().clean()
        customer_fields = cleaned_data.get('customer_fields', [])

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name and last_name:
            cleaned_data['full_name'] = f"{first_name} {last_name}"

        total_selected_fields = len(customer_fields)
        if total_selected_fields > 6:
            raise forms.ValidationError("You can select a maximum of 6 fields.")

        if not customer_fields and not cleaned_data.get('full_name'):
            raise forms.ValidationError("At least one field from the table or Full Name must be selected.")

        return cleaned_data


from django import forms
from .models import Meters, GenerationMeter, GenerationCT

# class MeterForm(forms.ModelForm):
#     class Meta:
#         model = Meters
#         fields = ['company_name', 'make', 'capacity', 'serial_number']
#
#
# class GenerationMeterForm(forms.ModelForm):
#     class Meta:
#         model = GenerationMeter
#         fields = ['company_name', 'make', 'capacity', 'serial_number']
#
# class GenerationCTForm(forms.ModelForm):
#     class Meta:
#         model = GenerationCT
#         fields = ['company_name', 'required', 'make', 'capacity', 'serial_number']

class GenerationMeterForm(forms.ModelForm):
    class Meta:
        model = GenerationMeter
        fields = ['comp_name', 'customer', 'make', 'capacity', 'serial_no']

class GenerationCTForm(forms.ModelForm):
    class Meta:
        model = GenerationCT
        fields = ['comp_name', 'customer', 'make', 'capacity', 'serial_no', 'required']


from django import forms


from django import forms
from .models import Meters, GenerationMeter, GenerationCT

from django import forms
from django.shortcuts import get_object_or_404
from .models import Meters, GenerationMeter, GenerationCT

from django import forms
from django.shortcuts import get_object_or_404
from .models import Meters, GenerationMeter, GenerationCT
from django import forms
from django.shortcuts import get_object_or_404
from .models import Meters, GenerationMeter, GenerationCT


class EditForm(forms.Form):
    comp_name = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, comp_name=None, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.fields['comp_name'].initial = comp_name
        self.model_fields = {}

        for model in [Meters, GenerationMeter, GenerationCT]:
            records = model.objects.filter(comp_name=comp_name)
            for record in records:
                for field in model._meta.fields:
                    field_name = f'{model.__name__.lower()}_{field.name}_{record.id}'
                    initial_value = getattr(record, field.name)
                    self.fields[field_name] = forms.CharField(
                        label=f'{model.__name__} - {field.name}',
                        initial=initial_value,
                        required=False
                    )
                    self.model_fields[field_name] = {'model': model, 'record_id': record.id}
                # Add checkbox field for record deletion
                self.fields[f'{model.__name__.lower()}_delete_{record.id}'] = forms.BooleanField(
                    label=f'Delete {model.__name__} - {record.id}',
                    required=False
                )

    def clean(self):
        cleaned_data = super().clean()
        for key, value in cleaned_data.items():
            if key.endswith('_id'):
                if not value or not value.isdigit():
                    raise forms.ValidationError(f"Invalid record ID for field {key}")
        return cleaned_data

    def save(self):
        for key, value in self.cleaned_data.items():
            if key.endswith('_id'):
                model_name, field_name, record_id = key.rsplit('_', 2)
                model = self.model_fields[key]['model']
                record = get_object_or_404(model, id=record_id)
                setattr(record, field_name, value)
                record.save()

        # Delete records if corresponding checkbox is checked
        for key, value in self.cleaned_data.items():
            if key.startswith(('meters_delete', 'generationmeter_delete', 'generationct_delete')):
                model_name, record_id = key.rsplit('_', 1)
                model = self.model_fields[f'{model_name}_id_{record_id}']['model']
                if value:
                    record_id = int(record_id)
                    record = get_object_or_404(model, id=record_id)
                    record.delete()


from django import forms

# class EditForm(forms.Form):
#     comp_name = forms.CharField(widget=forms.HiddenInput())
#
#     def __init__(self, *args, **kwargs):
#         super(EditForm, self).__init__(*args, **kwargs)
#


def get_model_instance(model_name, record_id):
    # Return the instance of the model based on the name and ID
    if model_name == 'meters':
        return Meters.objects.get(id=record_id)
    elif model_name == 'generation_meters':
        return GenerationMeter.objects.get(id=record_id)
    elif model_name == 'generation_cts':
        return GenerationCT.objects.get(id=record_id)
    else:
        return None




