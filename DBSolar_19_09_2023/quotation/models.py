from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.utils import timezone
from django.db.models import Max

# Add consumer type choices
CONSUMER_TYPE_CHOICES = [
    ('Residential', 'Residential'),
    ('Commercial', 'Commercial'),
    ('Industrial', 'Industrial'),
    ('Government', 'Government'),
]

def money(v):
    if not isinstance(v, Decimal):
        v = Decimal(v)
    return v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

STRUCTURE_CHOICES = [
    ('GI Structure', 'GI Structure'),
    ('Tin Shade', 'Tin Shade'),
    ('MS Structure', 'MS Structure'),
]

INV_PHASE_CHOICES = [
    ('Single Phase', 'Single Phase'),
    ('Three Phase', 'Three Phase'),
]

TITLE_CHOICES = [
    ('Mr', 'Mr'),
    ('Ms', 'Ms'),
]


# ================== ADD THIS CUSTOM FIELD CLASS ==================
class BitVaryingBooleanField(models.Field):
    """
    Custom Django field to handle PostgreSQL bit varying(1) as boolean.
    """
    description = "Boolean stored as bit varying"

    def __init__(self, *args, **kwargs):
        kwargs['default'] = kwargs.get('default', False)
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        # For PostgreSQL, use bit varying(1)
        if connection.vendor == 'postgresql':
            return 'bit varying(1)'
        # For other databases, use boolean
        return 'boolean'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        # Convert PostgreSQL bit varying to boolean
        if connection.vendor == 'postgresql':
            if isinstance(value, str):
                # String like '1' or '0'
                return value == '1'
            elif isinstance(value, (bytes, bytearray)):
                # Bytes like b'1' or b'0'
                return value == b'1'
            elif isinstance(value, int):
                # Integer like 1 or 0
                return value == 1
            else:
                return bool(value)

        return bool(value)

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, bool):
            return value

        # Handle string values
        if isinstance(value, str):
            return value.lower() in ('1', 'true', 't', 'yes', 'y')

        # Handle integer values
        if isinstance(value, int):
            return value == 1

        # Handle bytes
        if isinstance(value, (bytes, bytearray)):
            return value == b'1'

        return bool(value)

    def get_prep_value(self, value):
        # Convert to Python boolean
        return self.to_python(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None

        # For PostgreSQL, return '1' for True, '0' for False
        if connection.vendor == 'postgresql':
            return '1' if self.to_python(value) else '0'

        # For other databases, return boolean
        return bool(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return str(int(value)) if value is not None else ''


# ================== END OF CUSTOM FIELD ==================



class SolarPanelCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class PlantCapacity(models.Model):
    capacity = models.DecimalField(max_digits=6, decimal_places=2, unique=True)

    def __str__(self):
        return f"{self.capacity} KW"



class InverterCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

#
# class QuotationProduct(models.Model):
#     name = models.CharField(max_length=255)
#     unit = models.CharField(max_length=50, blank=True)
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#     make = models.CharField(max_length=255, blank=True)
#     warranty = models.CharField(max_length=255, blank=True)
#     def __str__(self):
#         return self.name

class OtherItem(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name





class Representative(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('name', 'contact')  # optional but useful

    def __str__(self):
        if self.contact:
            return f"{self.name} — {self.contact}"
        return self.name


class TermsAndCondition(models.Model):
    content = models.TextField()
    has_yellow_background = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    show_in_quotation_form = models.BooleanField(
        default=True,
        help_text='When enabled, this term appears on create/edit quotation forms.',
    )
    default_selected = models.BooleanField(
        default=False,
        help_text='When enabled, pre-selected on new quotation forms.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50] + "..." if len(self.content) > 50 else self.content


class QuotationMaster(models.Model):
    """Singleton settings for quotation letterhead, subsidy notes, etc."""
    company_name = models.CharField(max_length=200, default='Heramb Industries')
    company_logo = models.ImageField(upload_to='quotation/master/', blank=True, null=True)
    gst_no = models.CharField(max_length=50, blank=True, help_text='Company GST number on quotation PDF.')
    pan_no = models.CharField(max_length=20, blank=True, help_text='Company PAN number on quotation PDF.')
    address = models.TextField(
        blank=True,
        help_text='Company address shown on quotation PDF footer / letterhead.',
    )
    from_address = models.TextField(
        blank=True,
        help_text='From-address block on quotation PDF.',
    )
    header_image = models.ImageField(upload_to='quotation/master/', blank=True, null=True)
    footer_image = models.ImageField(upload_to='quotation/master/', blank=True, null=True)
    subsidy_notes = models.TextField(
        blank=True,
        help_text='Subsidy note text shown on quotation PDF.',
    )
    PDF_TEMPLATE_STANDARD = 'quotation'
    PDF_TEMPLATE_INDUSTRIAL = 'industrial'
    PDF_TEMPLATE_STANDARD_INDUSTRIAL = 'standard_industrial'
    PDF_TEMPLATE_CHOICES = [
        (PDF_TEMPLATE_STANDARD, 'Standard Quotation'),
        (PDF_TEMPLATE_INDUSTRIAL, 'Industrial Quotation'),
        (PDF_TEMPLATE_STANDARD_INDUSTRIAL, 'Standard & Industrial Quotation'),
    ]
    default_pdf_template = models.CharField(
        max_length=40,
        choices=PDF_TEMPLATE_CHOICES,
        default=PDF_TEMPLATE_STANDARD,
        help_text='Default quotation PDF template used in the software.',
    )
    proposal_cover_image = models.ImageField(
        upload_to='quotation/master/',
        blank=True,
        null=True,
        help_text='Left-column cover photo for Standard & Industrial quotation.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quotation Master'
        verbose_name_plural = 'Quotation Master'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class QuotationBankDetail(models.Model):
    account_name = models.CharField(max_length=200, blank=True)
    gst_no = models.CharField(max_length=50, blank=True)
    pan_no = models.CharField(max_length=20, blank=True)
    account_no = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    branch_name = models.CharField(max_length=100, blank=True)
    show_in_quotation_form = models.BooleanField(
        default=True,
        help_text='Show this bank block on quotation PDF when selected as default.',
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.account_name or self.bank_name or f'Bank #{self.pk}'

#
# class Quotation(models.Model):
#     # NEW FIELD: Consumer Type
#     consumer_type = models.CharField(
#         max_length=20,
#         choices=CONSUMER_TYPE_CHOICES,
#         default='Residential'
#     )
#
#     # NEW FIELDS: Proposed System
#     dc_capacity = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         verbose_name="DC Capacity (kWp)"
#     )
#     ac_capacity = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         verbose_name="AC Capacity (kWh)"
#     )
#
#     # Add this field for electricity unit rate
#     electricity_unit_rate = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=Decimal('11.00'),
#         verbose_name="Electricity Unit Rate (₹/kWh)"
#     )
#
#
#     # system_na = models.BooleanField(
#     #     default=False,
#     #     verbose_name="N.A."
#     # )
#     # ========== CHANGE THIS LINE ==========
#     system_na = BitVaryingBooleanField(
#         default=False,
#         verbose_name="N.A."
#     )
#     # ======================================
#
#     # NEW FIELD: Title (Mr/Ms)
#     title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='Mr')
#
#     consumer_name = models.CharField(max_length=255)
#     consumer_address1 = models.CharField(max_length=255, blank=True)
#     consumer_address2 = models.CharField(max_length=255, blank=True)
#     consumer_no = models.CharField(max_length=50, blank=True)
#     consumer_mobile = models.CharField(max_length=20, blank=True)
#
#     quotation_no = models.CharField(max_length=20, unique=False, blank=True)
#     date = models.DateTimeField(default=timezone.now)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     # CHANGED: Now ForeignKey to PlantCapacity
#     plant_capacity_kw = models.ForeignKey(PlantCapacity, on_delete=models.PROTECT)
#
#     # plant_capacity_kw = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.30'))
#     employee_name = models.CharField(max_length=255, blank=True)
#
#     panel_companies = models.ManyToManyField(SolarPanelCompany, blank=True)
#     inverter_companies = models.ManyToManyField(InverterCompany, blank=True)
#
#     panel_qty = models.IntegerField(default=0)
#     inverter_qty = models.IntegerField(default=0)
#     panel_type = models.CharField(max_length=100, blank=True)
#     panel_capacity_watt = models.CharField(max_length=100, blank=True)
#     inv_phase = models.CharField(max_length=13, choices=INV_PHASE_CHOICES, default='1 Phase')
#     inv_capacity_kw = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.30'))
#     panel_company_names = models.TextField(blank=True)  # NEW
#     inverter_company_names = models.TextField(blank=True)  # NEW
#     # PANEL WARRANTY
#     panel_manufacturing_warranty = models.CharField(max_length=50, blank=True)
#     panel_performance_warranty = models.CharField(max_length=50, blank=True)
#
#     # INVERTER WARRANTY
#     inverter_warranty = models.CharField(max_length=50, blank=True)
#
#     # other_details = JSONField(default=dict, blank=True)
#     other_details = models.TextField(blank=True)
#
#     structure_type = models.CharField(max_length=50, choices=STRUCTURE_CHOICES, default='GI Structure')
#     structure_back_height_ft = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
#     structure_front_height_ft = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
#     structure_warranty = models.CharField(max_length=100, blank=True, null=True)
#
#     special_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#     gst_5_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
#     gst_18_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('18.00'))
#     gst_5_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#     gst_18_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#
#     net_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
#     final_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
#     # In Quotation model add:
#     representatives = models.ManyToManyField(Representative, blank=True)
#     representative_names = models.TextField(blank=True)  # a cached textual list used for the PDF (optional)
#
#     terms_conditions = models.ManyToManyField(TermsAndCondition, blank=True)
#     terms_conditions_text = models.TextField(blank=True)  # cached for PDF
#
#     def __str__(self):
#         return f"Quotation {self.quotation_no} - {self.consumer_name}"
#
#     def save(self, *args, **kwargs):
#         if not self.quotation_no:
#             # Get all quotation numbers and extract base numbers (before underscore for revisions)
#             all_quotations = Quotation.objects.exclude(quotation_no__isnull=True).exclude(quotation_no='')
#             max_base_no = 0
#
#             for q in all_quotations:
#                 # Extract base number (part before underscore if revision exists)
#                 base_no_str = q.quotation_no.split('_')[0]
#                 try:
#                     base_no = int(base_no_str)
#                     if base_no > max_base_no:
#                         max_base_no = base_no
#                 except (ValueError, TypeError):
#                     continue
#
#             # Increment from the maximum base number found
#             newno = max_base_no + 1 if max_base_no > 0 else 1000
#             self.quotation_no = str(newno)
#         #
#         # # Handle system_na field - Django tries to insert boolean, but DB expects bit varying
#         # # Store the value temporarily
#         # system_na_value = getattr(self, 'system_na', False)
#         # if hasattr(self, '_system_na_temp'):
#         #     system_na_value = self._system_na_temp
#         # else:
#         #     self._system_na_temp = system_na_value
#         #
#         # # Set system_na to False to satisfy NOT NULL constraint
#         # # We'll update it via raw SQL immediately after save
#         # self.system_na = False
#         #
#         # # Try to save - if it fails due to type mismatch, the view will handle it
#         # # For now, just save normally and update via raw SQL after
#         super().save(*args, **kwargs)
#
#         # Update system_na using raw SQL with proper bit varying cast
#         if self.pk and hasattr(self, '_system_na_temp'):
#             from django.db import connection
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE quotation_quotation
#                     SET system_na = (%s)::bit(1)::bit varying
#                     WHERE id = %s
#                 """, [1 if self._system_na_temp else 0, self.pk])
#             # Clean up temporary attribute
#             delattr(self, '_system_na_temp')
#
#     # def calculate_from_net(self):
#     #     gst5p = self.gst_5_percent / 100
#     #     gst18p = self.gst_18_percent / 100
#     #     base = self.net_amount
#     #     gst5 = base * Decimal('0.70') * gst5p
#     #     gst18 = base * Decimal('0.30') * gst18p
#     #     total = base + gst5 + gst18 - self.special_discount
#     #     self.gst_5_amount = money(gst5)
#     #     self.gst_18_amount = money(gst18)
#     #     self.final_amount = money(total)
#     #     self.save()
#     #
#     # def calculate_from_final(self):
#     #     gst5p = self.gst_5_percent / 100
#     #     gst18p = self.gst_18_percent / 100
#     #     gst_factor = (Decimal('0.70') * gst5p) + (Decimal('0.30') * gst18p)
#     #     base = self.final_amount / (Decimal('1.00') + gst_factor)
#     #     gst5 = base * Decimal('0.70') * gst5p
#     #     gst18 = base * Decimal('0.30') * gst18p
#     #     self.gst_5_amount = money(gst5)
#     #     self.gst_18_amount = money(gst18)
#     #     self.net_amount = money(base)
#     #     self.save()
#
#     # def calculate_from_net(self):
#     #     """
#     #     Correct GST calculation:
#     #     5% GST on 70% of net
#     #     18% GST on 30% of net
#     #     final = net + gst5 + gst18 - discount
#     #     """
#     #     net = Decimal(self.net_amount or 0)
#     #     discount = Decimal(self.special_discount or 0)
#     #
#     #     gst5 = (net * Decimal('0.70')) * Decimal('0.05')
#     #     gst18 = (net * Decimal('0.30')) * Decimal('0.18')
#     #
#     #     self.gst_5_amount = money(gst5)
#     #     self.gst_18_amount = money(gst18)
#     #
#     #     self.gst_5_percent = self.gst_5_amount
#     #     self.gst_18_percent = self.gst_18_amount
#     #
#     #     self.final_amount = money(net + gst5 + gst18 - discount)
#     #
#     #
#     # def calculate_from_final(self):
#     #     """
#     #     Reverse GST calculation:
#     #     Determine base amount from final = base * (1 + GST%)
#     #     """
#     #
#     #     final_amt = Decimal(self.final_amount or 0)
#     #     discount = Decimal(self.special_discount or 0)
#     #
#     #     # combined effective GST = 3.5% + 5.4% = 8.9%
#     #     gst_factor = (Decimal('0.70') * Decimal('0.05')) + (Decimal('0.30') * Decimal('0.18'))
#     #
#     #     base = (final_amt + discount) / (1 + gst_factor)
#     #
#     #     gst5 = (base * Decimal('0.70')) * Decimal('0.05')
#     #     gst18 = (base * Decimal('0.30')) * Decimal('0.18')
#     #
#     #     self.net_amount = money(base)
#     #
#     #     self.gst_5_amount = money(gst5)
#     #     self.gst_18_amount = money(gst18)
#     #
#     #     self.gst_5_percent = self.gst_5_amount
#     #     self.gst_18_percent = self.gst_18_amount
#     #
#     #     self.final_amount = money(base + gst5 + gst18 - discount)
#
#
#     def calculate_from_net(self):
#         """
#         Correct GST calculation:
#         First apply discount, then calculate GST on the remaining amount
#         5% GST on 70% of (net - discount)
#         18% GST on 30% of (net - discount)
#         final = (net - discount) + gst5 + gst18
#         """
#         net = Decimal(self.net_amount or 0)
#         discount = Decimal(self.special_discount or 0)
#
#         # First apply discount
#         taxable_amount = net - discount
#
#         # Then calculate GST on taxable amount
#         gst5 = (taxable_amount * Decimal('0.70')) * Decimal('0.05')
#         gst18 = (taxable_amount * Decimal('0.30')) * Decimal('0.18')
#
#         self.gst_5_amount = money(gst5)
#         self.gst_18_amount = money(gst18)
#
#         self.gst_5_percent = self.gst_5_amount
#         self.gst_18_percent = self.gst_18_amount
#
#         # self.final_amount = money(taxable_amount + gst5 + gst18)
#         self.final_amount = round(taxable_amount + gst5 + gst18)
#
#     def calculate_from_final(self):
#         """
#         Reverse GST calculation:
#         Determine base taxable amount from final amount
#         """
#         final_amt = Decimal(self.final_amount or 0)
#         discount = Decimal(self.special_discount or 0)
#
#         # combined effective GST = 3.5% + 5.4% = 8.9%
#         gst_factor = (Decimal('0.70') * Decimal('0.05')) + (Decimal('0.30') * Decimal('0.18'))
#
#         # taxable_amount is the amount after discount but before GST
#         taxable_amount = final_amt / (1 + gst_factor)
#
#         # net amount before discount
#         base = taxable_amount + discount
#
#         gst5 = (taxable_amount * Decimal('0.70')) * Decimal('0.05')
#         gst18 = (taxable_amount * Decimal('0.30')) * Decimal('0.18')
#
#         self.net_amount = money(base)
#
#         self.gst_5_amount = money(gst5)
#         self.gst_18_amount = money(gst18)
#
#         self.gst_5_percent = self.gst_5_amount
#         self.gst_18_percent = self.gst_18_amount
#
#         # Final amount should match the input
#         # self.final_amount = money(taxable_amount + gst5 + gst18)
#         self.final_amount = round(taxable_amount + gst5 + gst18)


from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.db.models import JSONField

# Add this import if not already present
from django.contrib.postgres.fields import ArrayField


class Quotation(models.Model):
    # NEW FIELD: Consumer Type
    consumer_type = models.CharField(
        max_length=20,
        choices=CONSUMER_TYPE_CHOICES,
        default='Residential'
    )

    # NEW FIELDS: Proposed System
    dc_capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="DC Capacity (kWp)"
    )
    ac_capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="AC Capacity (kWh)"
    )

    # Add this field for electricity unit rate
    electricity_unit_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('11.00'),
        verbose_name="Electricity Unit Rate (₹/kWh)"
    )

    # ========== CHANGE THIS LINE ==========
    system_na = BitVaryingBooleanField(
        default=False,
        verbose_name="N.A."
    )
    # ======================================

    # NEW FIELD: Title (Mr/Ms)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='Mr')

    consumer_name = models.CharField(max_length=255)
    consumer_address1 = models.CharField(max_length=255, blank=True)
    consumer_address2 = models.CharField(max_length=255, blank=True)
    consumer_no = models.CharField(max_length=50, blank=True)
    consumer_mobile = models.CharField(max_length=20, blank=True)

    # NEW FIELDS: State and Email
    consumer_state = models.CharField(max_length=100, blank=True, verbose_name="State")
    consumer_email = models.EmailField(max_length=255, blank=True, verbose_name="Email ID")

    # NEW FIELD: Project Type
    project_type = models.CharField(
        max_length=50,
        choices=[
            ('RoofTop', 'RoofTop'),
            ('Ground Mount PV', 'Ground Mount PV'),
            ('Street Light', 'Street Light'),
            ('Water Pump', 'Water Pump'),
            ('Hi-Mas', 'Hi-Mas'),
            ('Other', 'Other'),
        ],
        blank=True,
        verbose_name="Project Type"
    )

    is_confirmed = models.BooleanField(default=False)
    # NEW FIELD: indicates whether quotation has been converted to a consumer record
    convert_consumer = models.BooleanField(default=False)

    PAYMENT_TYPE_CHOICES = [
        ('Full Payment', 'Full Payment'),
        ('Part Payment', 'Part Payment'),
        ('Part payment & remaning payment after subsidy',
         'Part payment & remaning payment after subsidy'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('Net Banking', 'Net Banking'),
        ('UPI', 'UPI'),
        ('Cash', 'Cash'),
        ('Hybrid', 'Hybrid'),
        ('Check', 'Check'),
    ]

    HYBRID_MODE_CHOICES = [
        ('UPI + Cash', 'UPI + Cash'),
        ('UPI + Net Banking', 'UPI + Net Banking'),
        ('UPI + BANK CHECK', 'UPI + BANK CHECK'),
    ]

    payment_type = models.CharField(
        max_length=80, choices=PAYMENT_TYPE_CHOICES,
        blank=True, null=True
    )

    payment_mode = models.CharField(
        max_length=50, choices=PAYMENT_MODE_CHOICES,
        blank=True, null=True
    )

    hybrid_mode = models.CharField(
        max_length=50, choices=HYBRID_MODE_CHOICES,
        blank=True, null=True
    )

    po_order_no = models.CharField(max_length=100, blank=True, null=True)
    po_date = models.DateField(blank=True, null=True)

    quotation_no = models.CharField(max_length=20, unique=False, blank=True)
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    # CHANGED: Now ForeignKey to PlantCapacity
    plant_capacity_kw = models.ForeignKey(PlantCapacity, on_delete=models.PROTECT)

    # plant_capacity_kw = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('3.30'))
    employee_name = models.CharField(max_length=255, blank=True)

    assigned_associate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_quotations',
        verbose_name='Assign Associate',
    )

    panel_companies = models.ManyToManyField(SolarPanelCompany, blank=True)
    inverter_companies = models.ManyToManyField(InverterCompany, blank=True)

    panel_qty = models.IntegerField(default=0)
    inverter_qty = models.IntegerField(default=0)
    panel_type = models.CharField(max_length=100, blank=True)
    panel_capacity_watt = models.CharField(max_length=100, blank=True)
    inv_phase = models.CharField(max_length=13, choices=INV_PHASE_CHOICES, default='1 Phase')
    inv_capacity_kw = models.DecimalField(max_digits=6, decimal_places=2)
    panel_company_names = models.TextField(blank=True)  # NEW
    inverter_company_names = models.TextField(blank=True)  # NEW
    # PANEL WARRANTY
    panel_manufacturing_warranty = models.CharField(max_length=50, blank=True)
    panel_performance_warranty = models.CharField(max_length=50, blank=True)

    # INVERTER WARRANTY
    inverter_warranty = models.CharField(max_length=50, blank=True)

    # other_details = JSONField(default=dict, blank=True)
    other_details = models.TextField(blank=True)

    structure_type = models.CharField(max_length=50, choices=STRUCTURE_CHOICES, default='GI Structure')
    structure_back_height_ft = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    structure_front_height_ft = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    structure_warranty = models.CharField(max_length=100, blank=True, null=True)

    special_discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    # When the user enters discount as % of basic/net; null when discount is only in rupees (special_discount).
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Discount (%)',
    )
    gst_5_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    gst_18_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('18.00'))
    gst_5_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gst_18_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    net_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    final_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    # In Quotation model add:
    representatives = models.ManyToManyField(Representative, blank=True)
    representative_names = models.TextField(blank=True)  # a cached textual list used for the PDF (optional)

    terms_conditions = models.ManyToManyField(TermsAndCondition, blank=True)
    terms_conditions_text = models.TextField(blank=True)  # cached for PDF

    # Lead CRM linkage + workflow (DB columns: lead_id, survey_id, created_by_id, approved_by_id,
    # approved_date, sent_date, sent_by_id, valid_until, status, version)
    QUOTATION_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('viewed', 'Viewed'),
        ('negotiating', 'Negotiating'),
        ('approved', 'Approved'),
        ('converted', 'Converted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    )

    lead = models.ForeignKey(
        'crm_leads.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='erp_quotations',
    )
    survey = models.ForeignKey(
        'surveys.Survey',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='erp_quotations',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations_created',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations_approved',
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations_sent',
    )
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=QUOTATION_STATUS_CHOICES,
        default='draft',
    )
    version = models.PositiveIntegerField(default=1)

    customer_approval = models.BooleanField(default=False)
    internal_approval = models.BooleanField(default=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='erp_quotations',
    )

    def __str__(self):
        return f"Quotation {self.quotation_no} - {self.consumer_name}"

    def get_list_date_display(self):
        """
        dd.mm.yyyy for list UIs. Handles DateTimeField/DateField values and legacy rows
        where the DB column may still be read as plain text.
        """
        from datetime import date, datetime

        out_fmt = '%d.%m.%Y'

        def coerce_to_display(value):
            if value is None or value == '':
                return None
            if isinstance(value, datetime):
                try:
                    return value.strftime(out_fmt)
                except (ValueError, OSError):
                    return None
            if isinstance(value, date):
                try:
                    return value.strftime(out_fmt)
                except (ValueError, OSError):
                    return None
            if isinstance(value, str):
                s = value.strip()
                if not s:
                    return None
                fmts = (
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%d-%m-%Y',
                    '%d/%m/%Y',
                    '%d.%m.%Y',
                    '%Y/%m/%d',
                )
                for fmt in fmts:
                    for n in (len(s), 26, 19, 10):
                        if n <= 0:
                            continue
                        try:
                            return datetime.strptime(s[:n], fmt).strftime(out_fmt)
                        except ValueError:
                            continue
            return None

        # Alias: some deployments still reference the old helper name in this loop.
        coerce_to_dd_mm_yyyy = coerce_to_display

        for attr in ('date', 'created_at'):
            text = coerce_to_dd_mm_yyyy(getattr(self, attr, None))
            if text:
                return text
        return '—'

    def save(self, *args, **kwargs):
        if not self.quotation_no:
            # Get all quotation numbers and extract base numbers (before underscore for revisions)
            all_quotations = Quotation.objects.exclude(quotation_no__isnull=True).exclude(quotation_no='')
            max_base_no = 0

            for q in all_quotations:
                # Extract base number (part before underscore if revision exists)
                base_no_str = q.quotation_no.split('_')[0]
                try:
                    base_no = int(base_no_str)
                    if base_no > max_base_no:
                        max_base_no = base_no
                except (ValueError, TypeError):
                    continue

            # Increment from the maximum base number found
            newno = max_base_no + 1 if max_base_no > 0 else 1000
            self.quotation_no = str(newno)
        super().save(*args, **kwargs)

        # Update system_na using raw SQL with proper bit varying cast
        if self.pk and hasattr(self, '_system_na_temp'):
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE quotation_quotation 
                    SET system_na = (%s)::bit(1)::bit varying
                    WHERE id = %s
                """, [1 if self._system_na_temp else 0, self.pk])
            # Clean up temporary attribute
            delattr(self, '_system_na_temp')

    def calculate_from_net(self):
        """
        Correct GST calculation:
        First apply discount, then calculate GST on the remaining amount
        5% GST on 70% of (net - discount)
        18% GST on 30% of (net - discount)
        final = (net - discount) + gst5 + gst18
        """
        net = Decimal(self.net_amount or 0)
        discount = Decimal(self.special_discount or 0)

        # First apply discount
        taxable_amount = net - discount

        # Then calculate GST on taxable amount
        gst5 = (taxable_amount * Decimal('0.70')) * Decimal('0.05')
        gst18 = (taxable_amount * Decimal('0.30')) * Decimal('0.18')

        self.gst_5_amount = money(gst5)
        self.gst_18_amount = money(gst18)

        self.gst_5_percent = self.gst_5_amount
        self.gst_18_percent = self.gst_18_amount

        # self.final_amount = money(taxable_amount + gst5 + gst18)
        self.final_amount = round(taxable_amount + gst5 + gst18)

    def calculate_from_final(self):
        """
        Reverse GST calculation:
        Determine base taxable amount from final amount
        """
        final_amt = Decimal(self.final_amount or 0)
        discount = Decimal(self.special_discount or 0)

        # combined effective GST = 3.5% + 5.4% = 8.9%
        gst_factor = (Decimal('0.70') * Decimal('0.05')) + (Decimal('0.30') * Decimal('0.18'))

        # taxable_amount is the amount after discount but before GST
        taxable_amount = final_amt / (1 + gst_factor)

        # net amount before discount
        base = taxable_amount + discount

        gst5 = (taxable_amount * Decimal('0.70')) * Decimal('0.05')
        gst18 = (taxable_amount * Decimal('0.30')) * Decimal('0.18')

        self.net_amount = money(base)

        self.gst_5_amount = money(gst5)
        self.gst_18_amount = money(gst18)

        self.gst_5_percent = self.gst_5_amount
        self.gst_18_percent = self.gst_18_amount

        # Final amount should match the input
        # self.final_amount = money(taxable_amount + gst5 + gst18)
        self.final_amount = round(taxable_amount + gst5 + gst18)


class QuotationRejectionRecord(models.Model):
    """Stored when CRM rejects an ERP quotation (reason from modal)."""

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='rejection_records',
        db_constraint=False,
    )
    reason = models.TextField()
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotation_rejection_records',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Rejection #{self.pk} — quotation {self.quotation_id}'


class QuotationApprovalRecord(models.Model):
    """Stored when CRM approves an ERP quotation from detail modal."""

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='approval_records',
        db_constraint=False,
    )
    status_snapshot = models.CharField(max_length=30, blank=True, default='approved')
    payment_type_snapshot = models.CharField(max_length=120, blank=True, default='')
    payment_mode_snapshot = models.CharField(max_length=120, blank=True, default='')
    hybrid_mode_snapshot = models.CharField(max_length=120, blank=True, default='')
    po_order_no_snapshot = models.CharField(max_length=120, blank=True, default='')
    po_date_snapshot = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotation_approval_records',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Approval #{self.pk} — quotation {self.quotation_id}'


class QuotationConversionRecord(models.Model):
    """Stored when CRM marks an ERP quotation as converted to consumer."""

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='conversion_records',
        db_constraint=False,
    )
    converted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotation_conversion_records',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Conversion #{self.pk} — quotation {self.quotation_id}'


# models.py (additions)


# class QuotationItem(models.Model):
#     quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(QuotationProduct, on_delete=models.PROTECT)
#     description = models.TextField(blank=True)
#     quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
#
#     def line_total(self):
#         return money(self.quantity * self.unit_price)
#
#     def __str__(self):
#         return f"{self.product.name} x {self.quantity}"
