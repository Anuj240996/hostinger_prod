# from django import forms
# from .models import Survey
# from apps.leads.models import Lead
# from django.contrib.auth.models import User
#
#
# class SurveyForm(forms.ModelForm):
#     class Meta:
#         model = Survey
#         fields = [
#             'lead', 'engineer', 'scheduled_date', 'status',
#             'feasibility', 'recommended_size', 'panel_count',
#             'inverter_capacity', 'estimated_generation', 'roof_area_required',
#             'has_shadow_issues', 'structural_feasible', 'technical_notes'
#         ]
#         widgets = {
#             'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'technical_notes': forms.Textarea(attrs={'rows': 4}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['lead'].queryset = Lead.objects.filter(stage__in=['qualified', 'survey'])
#         self.fields['engineer'].queryset = User.objects.filter(groups__name='Engineers')
#         self.fields['engineer'].required = False

from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Column
from crispy_forms.bootstrap import AppendedText

from .models import Survey
from apps.leads.models import Lead


def engineer_users_queryset():
    """
    Active users designated as engineers: ``Profile.department == 'Engineers'``
    (same as main DBSolar dashboard), or membership in Django group ``Engineers``.
    """
    return (
        User.objects.filter(is_active=True)
        .filter(Q(profile__department='Engineers') | Q(groups__name__iexact='Engineers'))
        .distinct()
        .order_by('first_name', 'last_name', 'username')
    )


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = [
            'lead', 'engineer', 'scheduled_date', 'status',
            'feasibility', 'recommended_size', 'panel_count',
            'inverter_capacity', 'estimated_generation', 'roof_area_required',
            'has_shadow_issues', 'structural_feasible', 'technical_notes'
        ]
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'technical_notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['status'].initial = 'in_progress'

        # New surveys: prefer qualified / survey leads. Edit: always include this survey's lead
        # (lead may be in quote/won/etc. after survey complete — otherwise save fails validation).
        leads_qs = Lead.objects.filter(stage__in=['qualified', 'survey'])
        if self.instance.pk and self.instance.lead_id:
            leads_qs = Lead.objects.filter(
                Q(stage__in=['qualified', 'survey']) | Q(pk=self.instance.lead_id)
            ).distinct()
        elif not leads_qs.exists():
            leads_qs = Lead.objects.all().order_by('-created')[:50]
            self.fields['lead'].help_text = (
                'No leads in Qualified/Survey stage. Showing recent leads.'
            )
        self.fields['lead'].queryset = leads_qs
        self.fields['lead'].empty_label = "Select a lead"

        engineer_qs = engineer_users_queryset()
        if self.instance.pk and self.instance.engineer_id:
            engineer_qs = User.objects.filter(
                Q(pk=self.instance.engineer_id)
                | Q(pk__in=engineer_qs.values_list('pk', flat=True))
            ).distinct().order_by('first_name', 'last_name', 'username')
        if not engineer_qs.exists():
            self.fields['engineer'].help_text = (
                'No engineers found. Set user Profile department to Engineers or add users to the Engineers group.'
            )
        self.fields['engineer'].queryset = engineer_qs
        self.fields['engineer'].empty_label = "Select an engineer (optional)"
        self.fields['engineer'].required = False

        # Units shown inline via AppendedText; drop duplicate model help_text.
        for fname in (
            'recommended_size',
            'inverter_capacity',
            'estimated_generation',
            'roof_area_required',
            'panel_count',
        ):
            self.fields[fname].help_text = ''

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        # Use Bootstrap `.row` (not `.form-row`) so the main theme grid reliably lays out two columns per row.
        self.helper.layout = Layout(
            Div(
                Column('lead', css_class='col-md-6 mb-3'),
                Column('engineer', css_class='col-md-6 mb-3'),
                css_class='row',
            ),
            Div(
                Column('scheduled_date', css_class='col-md-6 mb-3'),
                Column('status', css_class='col-md-6 mb-3'),
                css_class='row',
            ),
            Div(
                Column('feasibility', css_class='col-md-6 mb-3'),
                Column(AppendedText('panel_count', 'panels'), css_class='col-md-6 mb-3'),
                css_class='row',
            ),
            Div(
                Column(AppendedText('recommended_size', 'kW'), css_class='col-md-6 mb-3'),
                Column(AppendedText('inverter_capacity', 'kW'), css_class='col-md-6 mb-3'),
                css_class='row',
            ),
            Div(
                Column(AppendedText('estimated_generation', 'kWh/day'), css_class='col-md-6 mb-3'),
                Column(AppendedText('roof_area_required', 'sq.ft'), css_class='col-md-6 mb-3'),
                css_class='row',
            ),
            Div(
                Column('has_shadow_issues', css_class='col-md-6 mb-3'),
                Column('structural_feasible', css_class='col-md-6 mb-3'),
                css_class='row',
            ),
            Div(
                Column('technical_notes', css_class='col-12 mb-3'),
                css_class='row',
            ),
        )


class SurveyImageForm(forms.Form):
    image = forms.ImageField()
    caption = forms.CharField(max_length=200, required=False)
    is_primary = forms.BooleanField(required=False)