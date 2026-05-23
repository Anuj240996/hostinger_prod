# from django import forms
# from .models import Quotation, QuotationItem
# from apps.leads.models import Lead
# from apps.surveys.models import Survey
#
#
# class QuotationForm(forms.ModelForm):
#     class Meta:
#         model = Quotation
#         fields = [
#             'lead', 'survey', 'system_size', 'panel_type', 'panel_count',
#             'inverter_type', 'mounting_type', 'warranty_years', 'estimated_generation',
#             'subtotal', 'gst_percentage', 'subsidy_amount',
#             'roi', 'payback_years', 'monthly_emi', 'monthly_savings',
#             'valid_until', 'terms_conditions', 'internal_notes'
#         ]
#         widgets = {
#             'valid_until': forms.DateInput(attrs={'type': 'date'}),
#             'terms_conditions': forms.Textarea(attrs={'rows': 4}),
#             'internal_notes': forms.Textarea(attrs={'rows': 3}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['lead'].queryset = Lead.objects.filter(stage__in=['qualified', 'survey', 'quote'])
#         self.fields['survey'].required = False
#         self.fields['survey'].queryset = Survey.objects.filter(status='completed')
#

from django import forms
from .models import Quotation, QuotationItem
from apps.leads.models import Lead
from apps.surveys.models import Survey

class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'lead', 'survey', 'system_size', 'panel_type', 'panel_count',
            'inverter_type', 'mounting_type', 'warranty_years', 'estimated_generation',
            'subtotal', 'gst_percentage', 'subsidy_amount',
            'roi', 'payback_years', 'monthly_emi', 'monthly_savings',
            'valid_until', 'terms_conditions', 'internal_notes'
        ]
        widgets = {
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'terms_conditions': forms.Textarea(attrs={'rows': 4}),
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'lead': 'Lead name',
            'survey': 'Survey',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lead queryset: leads in qualified, survey, or quote stage
        leads_qs = Lead.objects.filter(stage__in=['qualified', 'survey', 'quote'])
        if not leads_qs.exists():
            leads_qs = Lead.objects.all()[:10]
            self.fields['lead'].help_text = "No leads in Qualified/Survey/Quote stage. Showing recent leads."
        self.fields['lead'].queryset = leads_qs
        self.fields['lead'].empty_label = "Select a lead"

        lead_id = None
        if self.data and 'lead' in self.data:
            raw = (self.data.get('lead') or '').strip()
            if raw:
                lead_id = raw
        elif self.instance and self.instance.pk and self.instance.lead_id:
            lead_id = self.instance.lead_id
        elif self.initial.get('lead') is not None:
            lead_id = self.initial['lead']

        if lead_id:
            self.fields['survey'].queryset = Survey.objects.filter(
                lead_id=lead_id,
                completed_date__isnull=False,
            ).order_by('-scheduled_date')
        else:
            self.fields['survey'].queryset = Survey.objects.none()
        self.fields['survey'].empty_label = "Select a survey (optional)"
        self.fields['survey'].required = False

    def clean(self):
        cleaned = super().clean()
        lead = cleaned.get('lead')
        survey = cleaned.get('survey')
        if lead and survey and survey.lead_id != lead.id:
            self.add_error('survey', 'This survey does not belong to the selected lead.')
        return cleaned

class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['description', 'quantity', 'unit_price']