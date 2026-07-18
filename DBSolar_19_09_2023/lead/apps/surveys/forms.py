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
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q
import re
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Column

from .models import Survey
from apps.leads.models import Lead


class MultipleClearableFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageUploadField(forms.FileField):
    """Accept multiple images via getlist(); validation in SurveyCompletionForm.clean()."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleClearableFileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control',
        }))
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def clean(self, value, initial=None):
        return None


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
    """Schedule / edit survey — technical completion fields are on Mark Complete modal only."""

    class Meta:
        model = Survey
        fields = ['lead', 'engineer', 'scheduled_date', 'status', 'feasibility']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'text',
                'class': 'form-control crm-datetime-picker',
                'placeholder': 'DD/MM/YYYY hh:mm AM/PM',
                'autocomplete': 'off',
            }, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_date'].input_formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %I:%M %p',
            '%d/%m/%Y %I:%M%p',
            '%d/%m/%Y %H:%M',
        ]
        if not self.instance.pk:
            self.fields['status'].initial = 'in_progress'

        leads_qs = Lead.objects.filter(stage='qualified')
        if self.instance.pk and self.instance.lead_id:
            leads_qs = Lead.objects.filter(
                Q(stage='qualified') | Q(pk=self.instance.lead_id)
            ).distinct()
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
        self.fields['engineer'].label_from_instance = self._engineer_label

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
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
                css_class='row',
            ),
        )

    @staticmethod
    def _engineer_label(user):
        full_name = user.get_full_name().strip() if user else ''
        return full_name or user.username


def compute_roof_area_sqft_from_walls(cleaned):
    """Area = one N/S length × one E/W length when exactly one side per axis is selected."""
    from decimal import Decimal, InvalidOperation

    def _len(key):
        val = cleaned.get(key)
        if val in (None, ''):
            return None
        try:
            d = Decimal(str(val))
            return d if d > 0 else None
        except (InvalidOperation, TypeError, ValueError):
            return None

    ns_len = None
    ew_len = None
    if cleaned.get('area_use_north'):
        ns_len = _len('length_north_ft')
    elif cleaned.get('area_use_south'):
        ns_len = _len('length_south_ft')
    if cleaned.get('area_use_east'):
        ew_len = _len('length_east_ft')
    elif cleaned.get('area_use_west'):
        ew_len = _len('length_west_ft')
    if ns_len is not None and ew_len is not None:
        return (ns_len * ew_len).quantize(Decimal('0.01'))
    return None


class SurveyCompletionForm(forms.ModelForm):
    """Technical survey results — submitted from Mark Complete modal on survey detail."""
    completion_images = MultipleImageUploadField(
        label='Survey photos (max 3)',
        help_text='Upload up to 3 photos. Images will be resized/compressed automatically.',
    )

    class Meta:
        model = Survey
        fields = [
            'recommended_size',
            'panel_count',
            'inverter_capacity',
            'estimated_generation',
            'roof_area_required',
            'building_height',
            'length_north_ft',
            'length_south_ft',
            'length_east_ft',
            'length_west_ft',
            'area_use_north',
            'area_use_south',
            'area_use_east',
            'area_use_west',
            'structure_type',
            'structure_back_height_ft',
            'structure_front_height_ft',
            'structure_leg_count',
            'structure_rafter_count',
            'structure_purlin_count',
            'structure_solar_panel_count',
            'structure_has_walkway',
            'structure_has_ladder',
            'structure_square_pipe_count',
            'has_shadow_issues',
            'structural_feasible',
            'technical_notes',
        ]
        widgets = {
            'technical_notes': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'recommended_size': 'Recommended / project size',
            'estimated_generation': 'Estimated Yearly generation',
            'roof_area_required': 'Total Roof Area',
            'building_height': 'Building Height',
            'panel_count': 'Panel capacity',
            'structure_type': 'Structure type',
            'structure_back_height_ft': 'Structure back height',
            'structure_front_height_ft': 'Structure front height',
            'structure_leg_count': 'No. of solar structure legs',
            'structure_rafter_count': 'No. of rafters',
            'structure_purlin_count': 'No. of purlins',
            'structure_solar_panel_count': 'No. of solar panels on structure',
            'structure_has_walkway': 'Walkway (optional)',
            'structure_has_ladder': 'Ladder (optional)',
            'structure_square_pipe_count': 'Square pipe quantity',
            'has_shadow_issues': 'Has shadow issues',
            'structural_feasible': 'Structure feasible',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_attrs = {'class': 'form-control'}
        for fname in (
            'recommended_size',
            'inverter_capacity',
            'estimated_generation',
            'roof_area_required',
            'building_height',
            'length_north_ft',
            'length_south_ft',
            'length_east_ft',
            'length_west_ft',
            'panel_count',
            'structure_back_height_ft',
            'structure_front_height_ft',
        ):
            self.fields[fname].help_text = ''
            self.fields[fname].widget.attrs.update(input_attrs)
        for fname in ('structure_leg_count', 'structure_rafter_count', 'structure_purlin_count', 'structure_solar_panel_count'):
            self.fields[fname].help_text = ''
            self.fields[fname].widget.attrs.update({
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'step': '1',
            })
        self.fields['structure_rafter_count'].widget.attrs.update({
            'readonly': 'readonly',
            'class': 'form-control bg-light',
            'title': 'Auto-calculated from legs (+2 when walkway is selected)',
        })
        self.fields['structure_square_pipe_count'].help_text = ''
        self.fields['structure_square_pipe_count'].widget.attrs.update({
            'class': 'form-control',
            'min': '1',
            'max': '100',
            'step': '1',
        })
        self.fields['structure_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['structure_type'].empty_label = '--- Select structure type ---'
        self.fields['technical_notes'].widget.attrs.update({'class': 'form-control', 'rows': 4})
        for cb in ('has_shadow_issues', 'structural_feasible', 'structure_has_walkway', 'structure_has_ladder'):
            self.fields[cb].widget.attrs.update({'class': 'form-check-input'})
        self.fields['structure_has_walkway'].widget.attrs.update({
            'class': 'form-check-input js-structure-walkway',
        })
        self.fields['structure_has_ladder'].widget.attrs.update({
            'class': 'form-check-input js-structure-ladder',
        })
        for cb in ('area_use_north', 'area_use_south', 'area_use_east', 'area_use_west'):
            self.fields[cb].widget.attrs.update({'class': 'form-check-input js-area-side-check'})
        for fname in ('length_north_ft', 'length_south_ft', 'length_east_ft', 'length_west_ft'):
            self.fields[fname].widget.attrs.update({'class': 'form-control js-wall-length-ft'})
        self.fields['recommended_size'].widget.attrs.update({
            'oninput': 'window.updateEstimatedYearlyGeneration && window.updateEstimatedYearlyGeneration()',
            'onchange': 'window.updateEstimatedYearlyGeneration && window.updateEstimatedYearlyGeneration()',
        })
        self.fields['estimated_generation'].widget.attrs.update({
            'step': '1',
            'min': '0',
        })
        self.fields['panel_count'].widget.attrs.update({
            'placeholder': 'e.g. 550 or 540-550',
            'inputmode': 'numeric',
        })

        # Layout rendered in survey_detail.html (input + unit on one row, not merged).
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('area_use_north') and cleaned.get('area_use_south'):
            raise forms.ValidationError('Select North or South, not both.')
        if cleaned.get('area_use_east') and cleaned.get('area_use_west'):
            raise forms.ValidationError('Select East or West, not both.')
        area_checks = sum(
            1 for k in ('area_use_north', 'area_use_south', 'area_use_east', 'area_use_west') if cleaned.get(k)
        )
        computed_area = compute_roof_area_sqft_from_walls(cleaned)
        if computed_area is not None:
            cleaned['roof_area_required'] = computed_area
        elif area_checks == 2:
            raise forms.ValidationError(
                'Enter lengths (ft) for the selected North/South and East/West sides to calculate roof area.'
            )
        structure_type = cleaned.get('structure_type')
        if structure_type in Survey.STRUCTURE_TYPES_REQUIRING_HEIGHT:
            for field in ('structure_back_height_ft', 'structure_front_height_ft'):
                if cleaned.get(field) in (None, ''):
                    self.add_error(field, 'This field is required for the selected structure type.')
        else:
            cleaned['structure_back_height_ft'] = None
            cleaned['structure_front_height_ft'] = None
            cleaned['structure_leg_count'] = None
            cleaned['structure_rafter_count'] = None
            cleaned['structure_purlin_count'] = None
            cleaned['structure_solar_panel_count'] = None
            cleaned['structure_has_walkway'] = False
            cleaned['structure_has_ladder'] = False
            cleaned['structure_square_pipe_count'] = None

        if not cleaned.get('structure_has_ladder'):
            cleaned['structure_square_pipe_count'] = None
        elif cleaned.get('structure_type') in Survey.STRUCTURE_TYPES_REQUIRING_HEIGHT and cleaned.get('structure_has_ladder'):
            if cleaned.get('structure_square_pipe_count') in (None, ''):
                self.add_error('structure_square_pipe_count', 'Enter square pipe quantity when ladder is selected.')

        files = []
        if self.files:
            files = self.files.getlist('completion_images')
        self.uploaded_completion_images = files
        remove_raw = (self.data.get('remove_photo_ids') or '').strip()
        remove_ids = []
        if remove_raw:
            remove_ids = [rid for rid in remove_raw.split(',') if rid.isdigit()]
        self.remove_photo_ids = remove_ids

        if self.instance and self.instance.pk:
            existing = self.instance.roof_images.count()
            remaining_existing = max(0, existing - len(remove_ids))
            if remaining_existing + len(files) > 3:
                raise ValidationError(
                    f'You can upload maximum 3 photos total ({remaining_existing} remaining, {len(files)} selected).'
                )
        elif len(files) > 3:
            raise ValidationError('You can upload maximum 3 photos.')
        allowed_types = ('image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp')
        for f in files:
            ctype = getattr(f, 'content_type', '') or ''
            if ctype and ctype not in allowed_types and not ctype.startswith('image/'):
                raise ValidationError(f'"{getattr(f, "name", "file")}" is not a valid image.')
        return cleaned

    def clean_panel_count(self):
        value = (self.cleaned_data.get('panel_count') or '').strip()
        if not value:
            return ''

        normalized = re.sub(r'\s+', '', value)
        if not re.fullmatch(r'\d+(?:-\d+)?', normalized):
            raise forms.ValidationError('Enter panel capacity like 550 or 540-550.')

        if '-' in normalized:
            start_s, end_s = normalized.split('-', 1)
            start_n = int(start_s)
            end_n = int(end_s)
            if start_n > end_n:
                raise forms.ValidationError('Panel capacity range must be low-high (e.g. 540-550).')

        return normalized

    def save(self, commit=True):
        survey = super().save(commit=False)
        if self.is_bound:
            survey.has_shadow_issues = 'has_shadow_issues' in self.data
            survey.structural_feasible = 'structural_feasible' in self.data
            survey.area_use_north = 'area_use_north' in self.data
            survey.area_use_south = 'area_use_south' in self.data
            survey.area_use_east = 'area_use_east' in self.data
            survey.area_use_west = 'area_use_west' in self.data
            survey.structure_has_walkway = 'structure_has_walkway' in self.data
            survey.structure_has_ladder = 'structure_has_ladder' in self.data
            if survey.structure_type not in Survey.STRUCTURE_TYPES_REQUIRING_HEIGHT:
                survey.structure_back_height_ft = None
                survey.structure_front_height_ft = None
                survey.structure_leg_count = None
                survey.structure_rafter_count = None
                survey.structure_purlin_count = None
                survey.structure_solar_panel_count = None
                survey.structure_has_walkway = False
                survey.structure_has_ladder = False
                survey.structure_square_pipe_count = None
            elif not survey.structure_has_ladder:
                survey.structure_square_pipe_count = None
        if commit:
            survey.save()
        return survey


class SurveyImageForm(forms.Form):
    image = forms.ImageField()
    caption = forms.CharField(max_length=200, required=False)
    is_primary = forms.BooleanField(required=False)