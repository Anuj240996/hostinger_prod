# from django import forms
# from .models import Quotation, STRUCTURE_CHOICES, INV_PHASE_CHOICES, SolarPanelCompany, InverterCompany, Representative, \
#     TITLE_CHOICES
# from .models import Quotation, OtherItem, SolarPanelCompany, InverterCompany, STRUCTURE_CHOICES, INV_PHASE_CHOICES
# #
# PANEL_TYPE_CHOICES = [
#     ('Bifacial DCR', 'Bifacial DCR'),
#     ('Bifacial NDCR', 'Bifacial NDCR'),
#     ('TOPCon DCR', 'TOPCon DCR'),
#     ('TOPCon NDCR', 'TOPCon NDCR'),
#     ('Mono PERC DCR', 'Mono PERC DCR'),
#     ('Mono PERC NDCR', 'Mono PERC NDCR'),
#     ('Poly DCR', 'Poly DCR'),
#     ('Poly NDCR', 'Poly NDCR'),
#     ('HJT DCR', 'HJT DCR'),
#     ('HJT NDCR', 'HJT NDCR'),
# ]
#
# PRICING_MODE_CHOICES = [
#     ('net', 'Net Amount'),
#     ('final', 'Final Amount'),
# ]
#
# # OTHER_CHOICES = [
# #         ('Walkway', 'Walkway'),
# #         ('Staircase', 'Staircase'),
# #         ('Plumbing', 'Plumbing'),
# #         ('Safety Railing', 'Safety Railing'),
# #         ('GI Tray', 'GI Tray'),
# #     ]
# #
# # class QuotationForm(forms.ModelForm):
# #     plant_capacity_kw = forms.ChoiceField(choices=[('3.3','3.3 kW'), ('5','5 kW'), ('10','10 kW')])
# #     panel_type = forms.ChoiceField(choices=PANEL_TYPE_CHOICES)
# #     inv_phase = forms.ChoiceField(choices=INV_PHASE_CHOICES)
# #     structure_type = forms.ChoiceField(choices=STRUCTURE_CHOICES)
# #     pricing_mode = forms.ChoiceField(choices=PRICING_MODE_CHOICES, required=True)
# #     net_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
# #     final_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
# #
# #     panel_manufacturing_warranty = forms.CharField(required=False)
# #     panel_performance_warranty = forms.CharField(required=False)
# #
# #     inverter_warranty = forms.CharField(required=False)
# #     structure_warranty = forms.CharField(required=False)
# #
# #     # other fields unchanged...
# #     other_items = forms.ModelMultipleChoiceField(
# #         queryset=OtherItem.objects.all().order_by('name'),
# #         required=False,
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #
# #     panel_companies = forms.ModelMultipleChoiceField(
# #         queryset=SolarPanelCompany.objects.all(),
# #         required=False,
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #
# #     inverter_companies = forms.ModelMultipleChoiceField(
# #         queryset=InverterCompany.objects.all(),
# #         required=False,
# #         widget=forms.CheckboxSelectMultiple
# #     )
# #
# #     class Meta:
# #         model = Quotation
# #         # fields = [
# #         #     'consumer_name', 'consumer_address1', 'consumer_address2', 'consumer_no', 'consumer_mobile',
# #         #     'date', 'plant_capacity_kw', 'employee_name',
# #         #     'panel_type', 'panel_capacity_watt',
# #         #     'inv_phase', 'inv_capacity_kw',
# #         #     'panel_companies',  # <-- ADD
# #         #     'inverter_companies',  # <-- ADD
# #         #     'structure_type', 'structure_back_height_ft', 'structure_front_height_ft',
# #         #     'special_discount', 'gst_5_percent', 'gst_18_percent'
# #         # ]
# #         fields = [
# #             'consumer_name', 'consumer_address1', 'consumer_address2',
# #             'consumer_no', 'consumer_mobile', 'date', 'plant_capacity_kw', 'employee_name',
# #
# #             'panel_type', 'panel_capacity_watt',
# #             'panel_manufacturing_warranty', 'panel_performance_warranty',
# #
# #             'inv_phase', 'inv_capacity_kw', 'inverter_warranty',
# #
# #             'panel_companies', 'inverter_companies',
# #
# #             'structure_type', 'structure_back_height_ft', 'structure_front_height_ft',
# #
# #             # 'walkway', 'staircase', 'plumbing', 'safety_railing', 'gi_tray',
# #
# #             'special_discount', 'gst_5_percent', 'gst_18_percent',
# #             'other_items', 'structure_warranty',
# #         ]
# #         widgets = {
# #             'date': forms.DateInput(attrs={'type': 'date'}),
# #         }
# class QuotationForm(forms.ModelForm):
#     # NEW: Title field as radio buttons
#     title = forms.ChoiceField(
#         choices=TITLE_CHOICES,
#         widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
#         initial='Mr'
#     )
#
#     plant_capacity_kw = forms.ChoiceField(choices=[('3.3','3.3 kW'), ('5','5 kW'), ('10','10 kW')])
#     panel_type = forms.ChoiceField(choices=PANEL_TYPE_CHOICES)
#     inv_phase = forms.ChoiceField(choices=INV_PHASE_CHOICES)
#     structure_type = forms.ChoiceField(choices=STRUCTURE_CHOICES)
#     pricing_mode = forms.ChoiceField(choices=PRICING_MODE_CHOICES, required=True)
#     net_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
#     final_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
#
#     panel_manufacturing_warranty = forms.CharField(required=False)
#     panel_performance_warranty = forms.CharField(required=False)
#
#     panel_qty = forms.IntegerField(required=False)
#     inverter_qty = forms.IntegerField(required=False)
#
#     inverter_warranty = forms.CharField(required=False)
#     structure_warranty = forms.CharField(required=False)
#
#     # form.py (inside QuotationForm)
#
#     representatives = forms.ModelMultipleChoiceField(
#         queryset=Representative.objects.all().order_by('name'),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     other_items = forms.ModelMultipleChoiceField(
#         queryset=OtherItem.objects.all().order_by('name'),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     panel_companies = forms.ModelMultipleChoiceField(
#         queryset=SolarPanelCompany.objects.all(),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     inverter_companies = forms.ModelMultipleChoiceField(
#         queryset=InverterCompany.objects.all(),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     class Meta:
#         model = Quotation
#         fields = [
#             'consumer_name', 'consumer_address1', 'consumer_address2', 'employee_name', 'panel_qty', 'inverter_qty',
#             'consumer_no', 'consumer_mobile', 'date', 'plant_capacity_kw',
#
#             'panel_type', 'panel_capacity_watt',
#             'panel_manufacturing_warranty', 'panel_performance_warranty',
#             'representatives',  # <-- add here
#             'inv_phase', 'inv_capacity_kw', 'inverter_warranty',
#
#             'panel_companies', 'inverter_companies',
#
#             'structure_type', 'structure_back_height_ft', 'structure_front_height_ft',
#
#             'special_discount', 'gst_5_percent', 'gst_18_percent',
#             'other_items', 'structure_warranty',
#         ]
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#         }
#
#     # ✅ Add this method
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         for field_name, field in self.fields.items():
#             # Skip checkbox groups
#             if isinstance(field.widget, forms.CheckboxSelectMultiple):
#                 continue
#
#             # Apply Bootstrap form-control
#             existing_classes = field.widget.attrs.get('class', '')
#             field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()
#
#
# #
# # class QuotationItemForm(forms.ModelForm):
# #     product = forms.ModelChoiceField(queryset=QuotationProduct.objects.all(), widget=forms.Select())
# #     class Meta:
# #         model = QuotationItem
# #         fields = ['product', 'description', 'quantity', 'unit_price']
# #         widgets = {
# #             'description': forms.TextInput(attrs={'placeholder': 'Short description (optional)'}),
# #             'quantity': forms.NumberInput(attrs={'step': '0.01'}),
# #             'unit_price': forms.NumberInput(attrs={'step': '0.01'}),
# #         }
#
#
#
#
# class SolarPanelCompanyForm(forms.ModelForm):
#     class Meta:
#         model = SolarPanelCompany
#         fields = ['name']
#
#
# class InverterCompanyForm(forms.ModelForm):
#     class Meta:
#         model = InverterCompany
#         fields = ['name']
from decimal import Decimal

from django import forms
from .models import Quotation, STRUCTURE_CHOICES, INV_PHASE_CHOICES, SolarPanelCompany, InverterCompany, Representative, \
    TermsAndCondition
from .models import Quotation, OtherItem, SolarPanelCompany, InverterCompany, STRUCTURE_CHOICES, INV_PHASE_CHOICES, PlantCapacity, TITLE_CHOICES, CONSUMER_TYPE_CHOICES

PANEL_TYPE_CHOICES = [
    ('Bifacial DCR', 'Bifacial DCR'),
    ('Bifacial NDCR', 'Bifacial NDCR'),
    ('TOPCon DCR', 'TOPCon DCR'),
    ('TOPCon NDCR', 'TOPCon NDCR'),
    ('Mono PERC DCR', 'Mono PERC DCR'),
    ('Mono PERC NDCR', 'Mono PERC NDCR'),
    ('Poly DCR', 'Poly DCR'),
    ('Poly NDCR', 'Poly NDCR'),
    ('HJT DCR', 'HJT DCR'),
    ('HJT NDCR', 'HJT NDCR'),
]

PRICING_MODE_CHOICES = [
    ('net', 'Net Amount'),
    ('final', 'Final Amount'),
]


# class QuotationForm(forms.ModelForm):
#     # NEW: Consumer Type field
#     consumer_type = forms.ChoiceField(
#         choices=CONSUMER_TYPE_CHOICES,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         initial='Residential'
#     )
#
#     # NEW: Title field as radio buttons
#     title = forms.ChoiceField(
#         choices=TITLE_CHOICES,
#         widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
#         initial='Mr'
#     )
#
#     # CHANGED: Now ModelChoiceField for plant capacity
#     plant_capacity_kw = forms.ModelChoiceField(
#         queryset=PlantCapacity.objects.all().order_by('capacity'),
#         empty_label="Select Plant Capacity",
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#
#     terms_conditions = forms.ModelMultipleChoiceField(
#         queryset=TermsAndCondition.objects.none(),  # Will be set in __init__
#         required=False,
#         widget=forms.CheckboxSelectMultiple,
#         label="Terms & Conditions"
#     )
#
#     panel_type = forms.ChoiceField(choices=PANEL_TYPE_CHOICES)
#     inv_phase = forms.ChoiceField(choices=INV_PHASE_CHOICES)
#     structure_type = forms.ChoiceField(choices=STRUCTURE_CHOICES)
#     pricing_mode = forms.ChoiceField(choices=PRICING_MODE_CHOICES, required=True)
#     net_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
#     final_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
#
#     panel_manufacturing_warranty = forms.CharField(required=False)
#     panel_performance_warranty = forms.CharField(required=False)
#
#     panel_qty = forms.IntegerField(required=False)
#     inverter_qty = forms.IntegerField(required=False)
#
#     inverter_warranty = forms.CharField(required=False)
#     structure_warranty = forms.CharField(required=False)
#
#     representatives = forms.ModelMultipleChoiceField(
#         queryset=Representative.objects.all().order_by('name'),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     other_items = forms.ModelMultipleChoiceField(
#         queryset=OtherItem.objects.all().order_by('name'),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     panel_companies = forms.ModelMultipleChoiceField(
#         queryset=SolarPanelCompany.objects.all(),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#
#     inverter_companies = forms.ModelMultipleChoiceField(
#         queryset=InverterCompany.objects.all(),
#         required=False,
#         widget=forms.CheckboxSelectMultiple
#     )
#     # NEW FIELDS: Proposed System
#     dc_capacity = forms.DecimalField(
#         required=False,
#         max_digits=10,
#         decimal_places=2,
#         widget=forms.NumberInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter DC Capacity in kWp',
#         })
#     )
#
#     ac_capacity = forms.DecimalField(
#         required=False,
#         max_digits=10,
#         decimal_places=2,
#         widget=forms.NumberInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Enter AC Capacity in kWh'
#         })
#     )
#
#     electricity_unit_rate = forms.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         initial=Decimal('11.00'),
#         label='Electricity Unit Rate (₹/kWh)',
#         widget=forms.NumberInput(attrs={
#             'class': 'form-control',
#             'step': '0.01',
#             'min': '0'
#         })
#     )
#
#     system_na = forms.BooleanField(
#         required=False,
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input',
#             'id': 'system_na_checkbox'
#         })
#     )
#
#     class Meta:
#         model = Quotation
#         fields = [
#             'consumer_type',  # NEW: Add consumer_type field
#             'title',  # NEW: Add title field
#             'consumer_name', 'consumer_address1', 'consumer_address2', 'employee_name', 'panel_qty', 'inverter_qty',
#             'consumer_no', 'consumer_mobile', 'date', 'plant_capacity_kw',
#             'panel_type', 'panel_capacity_watt',
#             'panel_manufacturing_warranty', 'panel_performance_warranty',
#             'representatives',
#             'inv_phase', 'inv_capacity_kw', 'inverter_warranty',
#             'panel_companies', 'inverter_companies',
#             'structure_type', 'structure_back_height_ft', 'structure_front_height_ft',
#             'special_discount', 'gst_5_percent', 'gst_18_percent',
#             'other_items', 'structure_warranty',
#             'terms_conditions',
#             'dc_capacity', 'ac_capacity', 'system_na',  # NEW: Add proposed system fields
#             'electricity_unit_rate',  # Add this line
#         ]
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         # Extract terms_conditions_queryset from kwargs if provided
#         terms_queryset = kwargs.pop('terms_conditions_queryset', None)
#
#         # CRITICAL: Format date field if instance is provided
#         # This ensures HTML5 date inputs get the correct YYYY-MM-DD format
#         instance = kwargs.get('instance', None)
#         if instance and hasattr(instance, 'date') and instance.date:
#             # Format date for HTML5 date input (YYYY-MM-DD format)
#             formatted_date = None
#             if hasattr(instance.date, 'strftime'):
#                 # It's a datetime object
#                 formatted_date = instance.date.strftime('%Y-%m-%d')
#             elif isinstance(instance.date, str):
#                 # It's already a string, try to parse and reformat
#                 try:
#                     from datetime import datetime
#                     # Try common date formats
#                     for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S%z']:
#                         try:
#                             parsed_date = datetime.strptime(instance.date, fmt)
#                             formatted_date = parsed_date.strftime('%Y-%m-%d')
#                             break
#                         except ValueError:
#                             continue
#                     # If parsing failed, use original string if it's already in YYYY-MM-DD format
#                     if not formatted_date and len(instance.date) >= 10:
#                         formatted_date = instance.date[:10]  # Take first 10 chars (YYYY-MM-DD)
#                 except Exception:
#                     formatted_date = instance.date
#             else:
#                 formatted_date = str(instance.date)
#
#             # Set formatted date in initial data if not already set
#             if formatted_date:
#                 if 'initial' in kwargs:
#                     kwargs['initial']['date'] = formatted_date
#                 else:
#                     kwargs['initial'] = {'date': formatted_date}
#
#         # CRITICAL: If terms_queryset is provided, set it on the CLASS base_fields BEFORE calling super()
#         # This ensures Django uses it during validation when instance is provided
#         original_base_queryset = None
#         if terms_queryset is not None:
#             # Set on the class, not the instance
#             original_base_queryset = QuotationForm.base_fields['terms_conditions'].queryset
#             QuotationForm.base_fields['terms_conditions'].queryset = terms_queryset
#
#         super().__init__(*args, **kwargs)
#
#         # IMPORTANT: Set queryset - use provided queryset if available, otherwise set to none
#         # This allows views to pass a custom queryset for validation
#         if terms_queryset is not None:
#             self.fields['terms_conditions'].queryset = terms_queryset
#             # Restore original base queryset to prevent side effects
#             if original_base_queryset is not None:
#                 QuotationForm.base_fields['terms_conditions'].queryset = original_base_queryset
#         else:
#             # Default: Always set to empty queryset to prevent database schema errors
#             # The view passes terms_conditions separately to the template, so the form
#             # field doesn't need to render them. The form field is only used for validation/saving.
#             # This prevents the "bit varying" boolean comparison error during widget rendering.
#             # The terms_conditions are displayed in the template using the list from the view.
#             self.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()
#
#         for field_name, field in self.fields.items():
#             # Skip checkbox groups and radio select
#             if isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
#                 continue
#
#             # Apply Bootstrap form-control
#             existing_classes = field.widget.attrs.get('class', '')
#             field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()

from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from .models import Quotation, STRUCTURE_CHOICES, INV_PHASE_CHOICES, SolarPanelCompany, InverterCompany, Representative, \
    TermsAndCondition
from .models import Quotation, OtherItem, SolarPanelCompany, InverterCompany, STRUCTURE_CHOICES, INV_PHASE_CHOICES, \
    PlantCapacity, TITLE_CHOICES, CONSUMER_TYPE_CHOICES

User = get_user_model()

PANEL_TYPE_CHOICES = [
    ('Bifacial DCR', 'Bifacial DCR'),
    ('Bifacial NDCR', 'Bifacial NDCR'),
    ('TOPCon DCR', 'TOPCon DCR'),
    ('TOPCon NDCR', 'TOPCon NDCR'),
    ('Mono PERC DCR', 'Mono PERC DCR'),
    ('Mono PERC NDCR', 'Mono PERC NDCR'),
    ('Poly DCR', 'Poly DCR'),
    ('Poly NDCR', 'Poly NDCR'),
    ('HJT DCR', 'HJT DCR'),
    ('HJT NDCR', 'HJT NDCR'),
]

PRICING_MODE_CHOICES = [
    ('net', 'Net Amount'),
    ('final', 'Final Amount'),
]


class AssociateModelChoiceField(forms.ModelChoiceField):
    """Dropdown shows First name + Last name (Django get_full_name), else username."""

    def label_from_instance(self, obj):
        name = (obj.get_full_name() or "").strip()
        return name if name else (obj.username or str(obj.pk))


# NEW: Project Type Choices
PROJECT_TYPE_CHOICES = [
    ('', 'Select Project Type'),
    ('RoofTop', 'RoofTop'),
    ('Ground Mount PV', 'Ground Mount PV'),
    ('Street Light', 'Street Light'),
    ('Water Pump', 'Water Pump'),
    ('Hi-Mas', 'Hi-Mas'),
    ('Other', 'Other'),
]


class QuotationForm(forms.ModelForm):
    # NEW: Consumer Type field
    consumer_type = forms.ChoiceField(
        choices=CONSUMER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='Residential'
    )

    # NEW: Title field as radio buttons
    title = forms.ChoiceField(
        choices=TITLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='Mr'
    )

    # CHANGED: Now ModelChoiceField for plant capacity
    plant_capacity_kw = forms.ModelChoiceField(
        queryset=PlantCapacity.objects.all().order_by('capacity'),
        empty_label="Select Plant Capacity",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    assigned_associate = AssociateModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label="Select Associate",
        label="Assign Associate Name",
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    terms_conditions = forms.ModelMultipleChoiceField(
        queryset=TermsAndCondition.objects.none(),  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Terms & Conditions"
    )

    panel_type = forms.ChoiceField(choices=PANEL_TYPE_CHOICES)
    inv_phase = forms.ChoiceField(choices=INV_PHASE_CHOICES)
    structure_type = forms.ChoiceField(choices=STRUCTURE_CHOICES)
    pricing_mode = forms.ChoiceField(choices=PRICING_MODE_CHOICES, required=True)
    net_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)
    final_amount_input = forms.DecimalField(required=False, max_digits=14, decimal_places=2)

    panel_manufacturing_warranty = forms.CharField(required=False)
    panel_performance_warranty = forms.CharField(required=False)

    panel_qty = forms.IntegerField(required=False)
    inverter_qty = forms.IntegerField(required=False)

    inverter_warranty = forms.CharField(required=False)
    structure_warranty = forms.CharField(required=False)

    representatives = forms.ModelMultipleChoiceField(
        queryset=Representative.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    other_items = forms.ModelMultipleChoiceField(
        queryset=OtherItem.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    panel_companies = forms.ModelMultipleChoiceField(
        queryset=SolarPanelCompany.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    inverter_companies = forms.ModelMultipleChoiceField(
        queryset=InverterCompany.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    # NEW FIELDS: Consumer State and Email
    consumer_state = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter State'
        })
    )

    consumer_email = forms.EmailField(
        required=False,
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email ID'
        })
    )

    # NEW FIELD: Project Type
    project_type = forms.ChoiceField(
        choices=PROJECT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # NEW FIELDS: Proposed System
    dc_capacity = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter DC Capacity in kWp',
        })
    )

    ac_capacity = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter AC Capacity in kWh'
        })
    )

    electricity_unit_rate = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=Decimal('11.00'),
        label='Electricity Unit Rate (₹/kWh)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )

    system_na = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'system_na_checkbox'
        })
    )

    class Meta:
        model = Quotation
        fields = [
            'consumer_type',  # NEW: Add consumer_type field
            'title',  # NEW: Add title field
            'consumer_name', 'consumer_address1', 'consumer_address2', 'employee_name', 'panel_qty', 'inverter_qty',
            'consumer_no', 'consumer_mobile', 'date', 'plant_capacity_kw', 'assigned_associate',
            'panel_type', 'panel_capacity_watt',
            'panel_manufacturing_warranty', 'panel_performance_warranty',
            'representatives',
            'inv_phase', 'inv_capacity_kw', 'inverter_warranty',
            'panel_companies', 'inverter_companies',
            'structure_type', 'structure_back_height_ft', 'structure_front_height_ft',
            'special_discount', 'gst_5_percent', 'gst_18_percent',
            'other_items', 'structure_warranty',
            'terms_conditions',
            'dc_capacity', 'ac_capacity', 'system_na',  # NEW: Add proposed system fields
            'electricity_unit_rate',  # Add this line
            'consumer_state', 'consumer_email', 'project_type',  # NEW: Add the new fields here
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Extract terms_conditions_queryset from kwargs if provided
        terms_queryset = kwargs.pop('terms_conditions_queryset', None)
        associate_queryset = kwargs.pop('associate_queryset', None)
        form_user = kwargs.pop('form_user', None)

        # CRITICAL: Format date field if instance is provided
        # This ensures HTML5 date inputs get the correct YYYY-MM-DD format
        instance = kwargs.get('instance', None)
        if instance and hasattr(instance, 'date') and instance.date:
            # Format date for HTML5 date input (YYYY-MM-DD format)
            formatted_date = None
            if hasattr(instance.date, 'strftime'):
                # It's a datetime object
                formatted_date = instance.date.strftime('%Y-%m-%d')
            elif isinstance(instance.date, str):
                # It's already a string, try to parse and reformat
                try:
                    from datetime import datetime
                    # Try common date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S%z']:
                        try:
                            parsed_date = datetime.strptime(instance.date, fmt)
                            formatted_date = parsed_date.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                    # If parsing failed, use original string if it's already in YYYY-MM-DD format
                    if not formatted_date and len(instance.date) >= 10:
                        formatted_date = instance.date[:10]  # Take first 10 chars (YYYY-MM-DD)
                except Exception:
                    formatted_date = instance.date
            else:
                formatted_date = str(instance.date)

            # Set formatted date in initial data if not already set
            if formatted_date:
                if 'initial' in kwargs:
                    kwargs['initial']['date'] = formatted_date
                else:
                    kwargs['initial'] = {'date': formatted_date}

        # CRITICAL: If terms_queryset is provided, set it on the CLASS base_fields BEFORE calling super()
        # This ensures Django uses it during validation when instance is provided
        original_base_queryset = None
        if terms_queryset is not None:
            # Set on the class, not the instance
            original_base_queryset = QuotationForm.base_fields['terms_conditions'].queryset
            QuotationForm.base_fields['terms_conditions'].queryset = terms_queryset

        # Indian-formatted amounts (with commas) from the browser fail Decimal validation — normalize before validation.
        data_kw = kwargs.get('data')
        if data_kw is not None:
            indian_amount_keys = (
                'net_amount_input',
                'final_amount_input',
                'special_discount',
                'gst_5_percent',
                'gst_18_percent',
            )
            post_copy = data_kw.copy()
            for key in indian_amount_keys:
                v = post_copy.get(key)
                if v is not None and v != '':
                    s = v[-1] if isinstance(v, (list, tuple)) else v
                    post_copy[key] = str(s).replace(',', '').strip()
            kwargs['data'] = post_copy

        super().__init__(*args, **kwargs)

        # IMPORTANT: Set queryset - use provided queryset if available, otherwise set to none
        # This allows views to pass a custom queryset for validation
        if terms_queryset is not None:
            self.fields['terms_conditions'].queryset = terms_queryset
            # Restore original base queryset to prevent side effects
            if original_base_queryset is not None:
                QuotationForm.base_fields['terms_conditions'].queryset = original_base_queryset
        else:
            self.fields['terms_conditions'].queryset = TermsAndCondition.objects.none()

        if 'assigned_associate' in self.fields:
            if associate_queryset is not None:
                self.fields['assigned_associate'].queryset = associate_queryset
            elif form_user is not None:
                from customer.staff_access import associate_users_for_quotation_dropdown
                self.fields['assigned_associate'].queryset = associate_users_for_quotation_dropdown(form_user)
            else:
                self.fields['assigned_associate'].queryset = User.objects.none()

        for field_name, field in self.fields.items():
            # Skip checkbox groups and radio select
            if isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                continue

            # assigned_associate already has form-control on widget
            if field_name == 'assigned_associate':
                continue

            # Apply Bootstrap form-control
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()

        # Pricing amounts: TextInput shows Indian comma grouping; DecimalField validates normalized POST data.
        indian_currency_fields = (
            'net_amount_input',
            'final_amount_input',
            'special_discount',
            'gst_5_percent',
            'gst_18_percent',
        )
        for fname in indian_currency_fields:
            if fname not in self.fields:
                continue
            fld = self.fields[fname]
            fld.widget = forms.TextInput(
                attrs={
                    'class': fld.widget.attrs.get('class', ''),
                    'inputmode': 'decimal',
                    'autocomplete': 'off',
                }
            )
            # Calculated GST on create only; keep editable when editing an existing quotation.
            if fname in ('gst_5_percent', 'gst_18_percent') and getattr(self.instance, 'pk', None) is None:
                fld.widget.attrs['readonly'] = True
                fld.widget.attrs['style'] = 'background:#f7f7f7;'


class SolarPanelCompanyForm(forms.ModelForm):
    class Meta:
        model = SolarPanelCompany
        fields = ['name']


class InverterCompanyForm(forms.ModelForm):
    class Meta:
        model = InverterCompany
        fields = ['name']

#
# class PlantCapacityForm(forms.ModelForm):
#     class Meta:
#         model = PlantCapacity
#         fields = ['capacity']
#         widgets = {
#             'capacity': forms.NumberInput(attrs={'step': '0.1', 'min': '0'})
#         }

class PlantCapacityForm(forms.ModelForm):
    capacity = forms.DecimalField(required=True, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert initial value 3.30 to 3.3
        if self.initial.get('capacity'):
            self.initial['capacity'] = self.initial['capacity'].normalize()
