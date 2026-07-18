# from django.db import models
# from django.contrib.auth.models import User
# from apps.core.models import TimeStampedModel
# from apps.leads.models import Lead
# from django.utils import timezone
#
#
# class Survey(TimeStampedModel):
#     STATUS_CHOICES = (
#         ('scheduled', 'Scheduled'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     )
#
#     FEASIBILITY_CHOICES = (
#         ('high', 'High'),
#         ('medium', 'Medium'),
#         ('low', 'Low'),
#     )
#
#     lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='surveys')
#     engineer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_surveys')
#     scheduled_date = models.DateTimeField()
#     completed_date = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
#
#     # Survey Details
#     feasibility = models.CharField(max_length=10, choices=FEASIBILITY_CHOICES, null=True, blank=True)
#     recommended_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
#     panel_count = models.IntegerField(null=True, blank=True)
#     inverter_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
#     estimated_generation = models.IntegerField(null=True, blank=True, help_text="kWh/day")
#     roof_area_required = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text="sq.ft")
#
#     # Analysis
#     has_shadow_issues = models.BooleanField(default=False)
#     structural_feasible = models.BooleanField(default=True)
#     technical_notes = models.TextField(blank=True)
#
#     # Metadata
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_surveys')
#     assigned_date = models.DateTimeField(null=True, blank=True)
#
#     class Meta:
#         ordering = ['-scheduled_date']
#
#     def __str__(self):
#         return f"Survey for {self.lead.name} - {self.scheduled_date.date()}"
#
#     @property
#     def is_today(self):
#         return self.scheduled_date.date() == timezone.now().date()
#
#     # @property
#     # def has_quotation(self):
#     #     return hasattr(self, 'quotation')
#
#     # @property
#     # def has_quotation(self):
#     #     from apps.quotations.models import Quotation
#     #     return Quotation.objects.filter(survey=self).exists()
#
#     @property
#     def has_quotation(self):
#         from apps.quotations.models import Quotation
#         return Quotation.objects.filter(survey=self).exists()
#
#
#
# class SurveyImage(TimeStampedModel):
#     survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='roof_images')
#     image = models.ImageField(upload_to='survey_images/')
#     caption = models.CharField(max_length=200, blank=True)
#     is_primary = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['-is_primary', 'created']
#
#     def __str__(self):
#         return f"Image for {self.survey.lead.name}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import TimeStampedModel, TenantAwareModel
from apps.leads.models import Lead
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Survey(TenantAwareModel, TimeStampedModel):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    FEASIBILITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    STRUCTURE_TYPE_CHOICES = (
        ('gi_structure', 'GI Structure'),
        ('ms_structure', 'MS Structure'),
        ('tin_shade', 'Tin Shade'),
        ('gi_tin_shade', 'GI With Tin Shade'),
        ('ms_tin_shade', 'MS with Tin Shade'),
        ('gi_ms_structure', 'GI with MS Structure'),
    )
    STRUCTURE_TYPES_REQUIRING_HEIGHT = frozenset({
        'gi_structure',
        'ms_structure',
        'gi_tin_shade',
        'ms_tin_shade',
        'gi_ms_structure',
    })

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='surveys')
    engineer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_surveys')
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    feasibility = models.CharField(max_length=10, choices=FEASIBILITY_CHOICES, null=True, blank=True)
    recommended_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
    panel_count = models.CharField(max_length=32, null=True, blank=True, help_text="W")
    inverter_capacity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kW")
    estimated_generation = models.IntegerField(null=True, blank=True, help_text="Units/year")
    roof_area_required = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text="sq.ft")
    building_height = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Mtr',
    )
    length_north_ft = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    length_south_ft = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    length_east_ft = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    length_west_ft = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    area_use_north = models.BooleanField(default=False)
    area_use_south = models.BooleanField(default=False)
    area_use_east = models.BooleanField(default=False)
    area_use_west = models.BooleanField(default=False)

    structure_type = models.CharField(
        max_length=32,
        choices=STRUCTURE_TYPE_CHOICES,
        null=True,
        blank=True,
    )
    structure_back_height_ft = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='ft',
    )
    structure_front_height_ft = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='ft',
    )
    structure_leg_count = models.PositiveIntegerField(null=True, blank=True)
    structure_rafter_count = models.PositiveIntegerField(null=True, blank=True)
    structure_purlin_count = models.PositiveIntegerField(null=True, blank=True)
    structure_solar_panel_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Physical PV modules mounted on structure (typically 1 per 2 purlins)',
    )
    structure_has_walkway = models.BooleanField(
        default=False,
        help_text='Optional walkway between panel rows (+2 rafters, +4 purlins)',
    )
    structure_has_ladder = models.BooleanField(
        default=False,
        help_text='Optional ladder attached to the walkway',
    )
    structure_square_pipe_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Square pipe quantity for ladder (shown when ladder is selected)',
    )

    has_shadow_issues = models.BooleanField(default=False)
    structural_feasible = models.BooleanField(default=True)
    technical_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_surveys')
    assigned_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"Survey for {self.lead.name} - {self.scheduled_date.date()}"

    @property
    def is_today(self):
        return self.scheduled_date.date() == timezone.now().date()

    @property
    def has_quotation(self):
        from apps.quotations.models import Quotation
        return Quotation.objects.filter(survey=self).exists()


class SurveyImage(TimeStampedModel):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='roof_images')
    image = models.ImageField(upload_to='survey_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'created']

    def __str__(self):
        return f"Image for {self.survey.lead.name}"

    def save(self, *args, **kwargs):
        """
        Store images in a smaller, consistent size to reduce DB/storage usage.
        Keeps aspect ratio, max 1280px on longest side, JPEG quality ~72 when possible.
        """
        if self.image and not kwargs.pop('skip_resize', False):
            try:
                if hasattr(self.image, 'seek'):
                    self.image.seek(0)
                img = Image.open(self.image)
                if hasattr(self.image, 'seek'):
                    self.image.seek(0)
                img_format = (img.format or '').upper()
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    img_format = 'JPEG'

                max_side = 1280
                w, h = img.size
                if max(w, h) > max_side:
                    img.thumbnail((max_side, max_side), Image.LANCZOS)

                buf = BytesIO()
                save_kwargs = {}
                if img_format in ('JPEG', 'JPG'):
                    save_kwargs.update({'format': 'JPEG', 'quality': 72, 'optimize': True})
                elif img_format == 'PNG':
                    save_kwargs.update({'format': 'PNG', 'optimize': True})
                else:
                    save_kwargs.update({'format': 'JPEG', 'quality': 72, 'optimize': True})
                    img_format = 'JPEG'

                img.save(buf, **save_kwargs)
                buf.seek(0)
                base_name = self.image.name.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
                if img_format == 'JPEG' and not base_name.lower().endswith(('.jpg', '.jpeg')):
                    base_name = base_name.rsplit('.', 1)[0] + '.jpg'
                self.image.save(base_name, ContentFile(buf.read()), save=False)
            except Exception:
                pass
        return super().save(*args, **kwargs)