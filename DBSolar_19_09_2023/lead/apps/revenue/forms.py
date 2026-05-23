from django import forms
from .models import Revenue, RevenueTarget
from apps.leads.models import Lead


class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['lead', 'amount', 'date', 'payment_status', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lead'].queryset = Lead.objects.filter(stage='won')
        self.fields['payment_method'].required = False
        self.fields['transaction_id'].required = False


class RevenueTargetForm(forms.ModelForm):
    class Meta:
        model = RevenueTarget
        fields = ['user', 'year', 'month', 'target_amount']