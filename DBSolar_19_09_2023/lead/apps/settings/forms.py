# from django import forms
# from apps.leads.models import LeadSource, Campaign
# from .models import LostReason, ScoringRule
# #
# # class LeadSourceForm(forms.ModelForm):
# #     class Meta:
# #         model = LeadSource
# #         fields = ['name', 'cost_per_lead', 'is_active']
# #         widgets = {
# #             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Website, Referral'}),
# #             'cost_per_lead': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
# #         }
#
# class CampaignForm(forms.ModelForm):
#     class Meta:
#         model = Campaign
#         fields = ['name', 'source', 'start_date', 'end_date', 'budget', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'source': forms.Select(attrs={'class': 'form-select'}),
#             'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }
#
# class LeadSourceForm(forms.ModelForm):
#     class Meta:
#         model = LeadSource
#         fields = ['name', 'cost_per_lead', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Website, Referral'}),
#             'cost_per_lead': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['cost_per_lead'].required = False
#
# class LostReasonForm(forms.ModelForm):
#     class Meta:
#         model = LostReason
#         fields = ['name', 'order', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Price too high'}),
#             'order': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
#         }
#
# class ScoringRuleForm(forms.ModelForm):
#     class Meta:
#         model = ScoringRule
#         fields = ['criteria', 'condition', 'value', 'points', 'is_active']
#         widgets = {
#             'criteria': forms.Select(attrs={'class': 'form-select'}),
#             'condition': forms.Select(attrs={'class': 'form-select'}),
#             'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5000'}),
#             'points': forms.NumberInput(attrs={'class': 'form-control', 'value': 10}),
#         }


from django import forms
from apps.leads.models import LeadSource, Campaign
from .models import LostReason, ScoringRule

from django import forms
from apps.leads.models import Campaign, LeadSource
# ... other imports

class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = ['name', 'cost_per_lead', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Website, Referral'}),
            'cost_per_lead': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cost_per_lead'].required = False

#
# class CampaignForm(forms.ModelForm):
#     class Meta:
#         model = Campaign
#         fields = ['name', 'source', 'start_date', 'end_date', 'budget', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'source': forms.Select(attrs={'class': 'form-select'}),
#             'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }

class CampaignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        if organization:
            self.fields['source'].queryset = LeadSource.objects.filter(organization=organization)

    class Meta:
        model = Campaign
        fields = ['name', 'source', 'start_date', 'end_date', 'budget', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
#
# class LostReasonForm(forms.ModelForm):
#     class Meta:
#         model = LostReason
#         fields = ['name', 'order', 'is_active']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Price too high'}),
#             'order': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
#         }

from django import forms
from .models import LostReason

class LostReasonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        self.fields['is_active'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if self.organization:
            name = cleaned_data.get('name')
            if name and LostReason.objects.filter(organization=self.organization, name=name).exists():
                if not self.instance.pk or self.instance.name != name:
                    raise forms.ValidationError({'name': 'A lost reason with this name already exists.'})
        return cleaned_data

    class Meta:
        model = LostReason
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Price too high'}),
        }
#
# class ScoringRuleForm(forms.ModelForm):
#     class Meta:
#         model = ScoringRule
#         fields = ['criteria', 'condition', 'value', 'points', 'is_active']
#         widgets = {
#             'criteria': forms.Select(attrs={'class': 'form-select'}),
#             'condition': forms.Select(attrs={'class': 'form-select'}),
#             'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5000'}),
#             'points': forms.NumberInput(attrs={'class': 'form-control', 'value': 10}),
#         }

class ScoringRuleForm(forms.ModelForm):
    class Meta:
        model = ScoringRule
        fields = ['criteria', 'condition', 'value', 'points', 'is_active']
        widgets = {
            'criteria': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5000'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'value': 10}),
        }