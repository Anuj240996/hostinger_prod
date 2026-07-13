from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from .models import Lead, LeadActivity, LeadSource, Campaign

User = get_user_model()


def _format_indian_amount(value):
    """Format decimal for edit-form display (Indian grouping, no symbol)."""
    if value is None or value == '':
        return ''
    try:
        dec = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return str(value)
    sign = '-' if dec < 0 else ''
    dec = abs(dec)
    if dec == dec.to_integral_value():
        digits = str(dec.to_integral_value())
    else:
        text = format(dec, 'f')
        whole, frac = text.split('.', 1)
        digits = whole
        frac = frac.rstrip('0')
        grouped = _group_indian(digits)
        return f'{sign}{grouped}.{frac}' if frac else f'{sign}{grouped}'
    return f'{sign}{_group_indian(digits)}'


def _group_indian(integer_digits):
    rev = integer_digits[::-1]
    groups = [rev[:3]]
    i = 3
    while i < len(rev):
        groups.append(rev[i:i + 2])
        i += 2
    return ','.join(groups)[::-1]


def _parse_indian_decimal(value):
    if value in (None, ''):
        return None
    if isinstance(value, Decimal):
        return value
    text = str(value).replace(',', '').replace('₹', '').replace('\u20b9', '').strip()
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        raise forms.ValidationError('Enter a valid amount.')


def lead_list_filter_sales_users_queryset():
    """Active staff (non-superuser), including associates, for Assigned to filters and lead forms."""
    return (
        User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
        .distinct()
        .order_by('first_name', 'last_name', 'username')
    )


def pipeline_quotation_filter_assigned_users_queryset(
    *, lead_queryset=None, quotation_queryset=None, selected_pk=None
):
    """
    Sales person dropdown for quotation list: users who appear as Lead.assigned_to
    or Quotation.assigned_associate on in-scope records (not the full staff list).
    """
    used_ids = set()
    leads = lead_queryset if lead_queryset is not None else Lead.objects.all()
    used_ids |= set(
        leads.exclude(assigned_to_id__isnull=True).values_list('assigned_to_id', flat=True)
    )
    if quotation_queryset is not None:
        used_ids |= set(
            quotation_queryset.exclude(assigned_associate_id__isnull=True).values_list(
                'assigned_associate_id', flat=True
            )
        )
    used_ids.discard(None)
    qs = User.objects.filter(pk__in=used_ids).order_by('first_name', 'last_name', 'username')
    if selected_pk:
        try:
            pk = int(selected_pk)
        except (TypeError, ValueError):
            pk = None
        if pk and not qs.filter(pk=pk).exists():
            qs = (
                User.objects.filter(Q(pk__in=qs.values('pk')) | Q(pk=pk))
                .distinct()
                .order_by('first_name', 'last_name', 'username')
            )
    return qs


def sales_user_queryset_with_fallback(current_pk):
    """
    Same users as lead_list_filter_sales_users_queryset; if current_pk is set
    and that user is outside the filtered set (e.g. inactive), include them so
    ModelChoiceField stays valid on edit.
    """
    base = lead_list_filter_sales_users_queryset()
    if current_pk and not base.filter(pk=current_pk).exists():
        return (
            User.objects.filter(Q(pk__in=base.values('pk')) | Q(pk=current_pk))
            .distinct()
            .order_by('first_name', 'last_name', 'username')
        )
    return base


def lead_assignee_engineers_queryset():
    """
    Staff engineers only: active + is_staff, and either main app Profile
    department ``Engineers`` or Django group ``Engineers`` (aligned with surveys).
    """
    return (
        User.objects.filter(is_active=True, is_staff=True)
        .filter(Q(profile__department='Engineers') | Q(groups__name__iexact='Engineers'))
        .distinct()
        .order_by('first_name', 'last_name', 'username')
    )


class LeadForm(forms.ModelForm):
    # Text inputs so Indian comma formatting works on edit (type=number rejects commas).
    electricity_bill = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'inputmode': 'decimal',
            'placeholder': '0',
            'autocomplete': 'off',
        }),
    )
    budget = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'inputmode': 'decimal',
            'placeholder': '0',
            'autocomplete': 'off',
        }),
    )
    estimated_value = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'inputmode': 'decimal',
            'placeholder': '0',
            'autocomplete': 'off',
        }),
    )

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        assign_pk = getattr(self.instance, 'assigned_to_id', None) if self.instance.pk else None
        self.fields['assigned_to'].queryset = sales_user_queryset_with_fallback(assign_pk)
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].label_from_instance = (
            lambda u: (u.get_full_name() or '').strip() or (u.username or '')
        )
        self.fields['longitude'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].label = 'Longitude'
        self.fields['latitude'].label = 'Latitude'
        self.fields['state'].label = 'State'
        self.fields['pincode'].label = 'Pin Code'
        self.fields['phone'].widget.attrs.update({
            'maxlength': '10',
            'minlength': '10',
            'inputmode': 'numeric',
            'pattern': r'[0-9]{10}',
            'placeholder': '10-digit mobile',
        })
        self.fields['pincode'].widget.attrs.update({
            'maxlength': '6',
            'minlength': '6',
            'inputmode': 'numeric',
            'pattern': r'[0-9]{6}',
            'placeholder': '6-digit pin',
            'class': 'form-control',
        })
        self.fields['rooftop_area'].label = 'Total Rooftop Area'
        self.fields['rooftop_area'].required = False
        self.fields['rooftop_area_unit'].label = ''
        self.fields['rooftop_area_unit'].required = False
        self.fields['electricity_bill'].label = 'Electricity Bill'
        self.fields['monthly_consumption'].label = 'Monthly Consumption'
        self.fields['monthly_consumption'].required = False
        self.fields['budget'].label = 'Budget'
        self.fields['estimated_value'].label = 'Estimated Value'
        self.fields['finance_type'].label = 'Finance'
        self.fields['finance_type'].required = False
        self.fields['finance_type'].choices = [('', '---------')] + list(Lead.FINANCE_TYPES)
        self.fields['next_followup'].label = 'Next Follow-up'
        self.fields['next_followup'].input_formats = [
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %I:%M %p',
            '%d/%m/%Y %I:%M%p',
            '%d/%m/%Y %I:%M %P',
        ]

        # Prefill money fields from DB in Indian format (edit page).
        if self.instance and self.instance.pk and not self.is_bound:
            self.fields['electricity_bill'].initial = _format_indian_amount(self.instance.electricity_bill)
            self.fields['budget'].initial = _format_indian_amount(self.instance.budget)
            self.fields['estimated_value'].initial = _format_indian_amount(self.instance.estimated_value)

        if organization:
            self.fields['source'].queryset = LeadSource.objects.filter(organization=organization, is_active=True)
            self.fields['campaign'].queryset = Campaign.objects.filter(organization=organization).order_by(
                'name'
            )
            self.fields['campaign'].empty_label = 'N.A.'
        else:
            self.fields['source'].queryset = LeadSource.objects.none()
            self.fields['campaign'].queryset = Campaign.objects.none()

    def clean_electricity_bill(self):
        return _parse_indian_decimal(self.cleaned_data.get('electricity_bill'))

    def clean_budget(self):
        return _parse_indian_decimal(self.cleaned_data.get('budget'))

    def clean_estimated_value(self):
        return _parse_indian_decimal(self.cleaned_data.get('estimated_value'))

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        digits = ''.join(ch for ch in phone if ch.isdigit())
        if len(digits) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return digits

    def clean_pincode(self):
        pincode = (self.cleaned_data.get('pincode') or '').strip()
        digits = ''.join(ch for ch in pincode if ch.isdigit())
        if len(digits) != 6:
            raise forms.ValidationError('Pin code must be exactly 6 digits.')
        return digits

    class Meta:
        model = Lead
        fields = [
            'name', 'phone', 'email', 'longitude', 'latitude',
            'address', 'city', 'state', 'pincode',
            'property_type', 'roof_type', 'electricity_bill',
            'rooftop_area', 'rooftop_area_unit', 'monthly_consumption',
            'source', 'campaign', 'score',
            'assigned_to', 'budget', 'estimated_value', 'finance_type',
            'next_followup', 'notes', 'internal_notes'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
            'next_followup': forms.DateTimeInput(attrs={
                'type': 'text',
                'class': 'form-control lead-schedule-input',
                'placeholder': 'DD/MM/YYYY hh:mm AM/PM',
                'autocomplete': 'off',
            }, format='%Y-%m-%dT%H:%M'),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'e.g. 78.9629', 'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'e.g. 20.5937', 'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '10',
                'minlength': '10',
                'inputmode': 'numeric',
                'pattern': '[0-9]{10}',
                'placeholder': '10-digit mobile',
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '6',
                'minlength': '6',
                'inputmode': 'numeric',
                'pattern': '[0-9]{6}',
                'placeholder': '6-digit pin',
            }),
            'rooftop_area': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'Area',
                'class': 'form-control lead-rooftop-input',
            }),
            'rooftop_area_unit': forms.Select(attrs={'class': 'form-select lead-rooftop-unit'}),
            'monthly_consumption': forms.NumberInput(attrs={
                'step': '1',
                'placeholder': '0',
                'class': 'form-control lead-consumption-input',
            }),
        }

class LeadActivityForm(forms.ModelForm):
    class Meta:
        model = LeadActivity
        fields = ['activity_type', 'description', 'metadata']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LeadFilterForm(forms.Form):
    date_range = forms.ChoiceField(choices=[
        ('', 'All Time'),
        ('today', 'Today'),
        ('yesterday', 'Yesterday'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('custom', 'Custom Range'),
    ], required=False)

    from_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    to_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
    )
    source = forms.ModelChoiceField(queryset=LeadSource.objects.filter(is_active=True), required=False)
    stage = forms.ChoiceField(choices=[('', 'All')] + list(Lead.STAGE_CHOICES), required=False)
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter city'}))
    score = forms.ChoiceField(choices=[('', 'All')] + list(Lead.SCORE_CHOICES), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = lead_list_filter_sales_users_queryset()
        self.fields['assigned_to'].label_from_instance = (
            lambda u: (u.get_full_name() or '').strip() or (u.username or '')
        )