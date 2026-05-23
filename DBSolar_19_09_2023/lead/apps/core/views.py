# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.db.models import Count, Sum, Avg
# from django.utils import timezone
# from datetime import timedelta
# import json
#
# from apps.leads.models import Lead, LeadActivity, FollowUp
# from django.contrib.auth.models import User
#
#
# @login_required
# def dashboard(request):
#     """
#     Main dashboard view with all KPIs and charts
#     """
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#
#     # KPI Calculations
#     total_leads = Lead.objects.filter(created__date__gte=first_day_month).count()
#     new_leads_today = Lead.objects.filter(created__date=today).count()
#
#     # Conversion Rate
#     total_won = Lead.objects.filter(stage='won', created__date__gte=first_day_month).count()
#     total_qualified = Lead.objects.filter(created__date__gte=first_day_month).exclude(stage='new').count()
#     conversion_rate = (total_won / total_qualified * 100) if total_qualified > 0 else 0
#
#     # Revenue (simulated for now - will be replaced with actual revenue model)
#     revenue_closed = Lead.objects.filter(
#         stage='won',
#         converted_at__date__gte=first_day_month
#     ).aggregate(total=Sum('estimated_value'))['total'] or 0
#
#     # Forecast Revenue (weighted pipeline)
#     leads_in_pipeline = Lead.objects.exclude(stage__in=['won', 'lost'])
#     forecast_revenue = sum(lead.weighted_value for lead in leads_in_pipeline)
#
#     # Follow-ups
#     followups_due = FollowUp.objects.filter(
#         scheduled_date__date=today,
#         status='scheduled'
#     ).count()
#
#     overdue_followups = FollowUp.objects.filter(
#         scheduled_date__date__lt=today,
#         status='scheduled'
#     ).count()
#
#     # Growth calculations (compare with previous month)
#     last_month = first_day_month - timedelta(days=1)
#     last_month_first = last_month.replace(day=1)
#
#     last_month_leads = Lead.objects.filter(
#         created__date__gte=last_month_first,
#         created__date__lt=first_day_month
#     ).count()
#
#     leads_growth = ((total_leads - last_month_leads) / last_month_leads * 100) if last_month_leads > 0 else 0
#
#     # Pipeline Funnel Data
#     funnel_data = {
#         'lead': Lead.objects.filter(stage='new').count(),
#         'qualified': Lead.objects.filter(stage='qualified').count(),
#         'survey': Lead.objects.filter(stage='survey').count(),
#         'quote': Lead.objects.filter(stage='quote').count(),
#         'won': Lead.objects.filter(stage='won').count(),
#     }
#
#     # Forecast Chart Data (next 6 months)
#     forecast_months = []
#     forecast_values = []
#     for i in range(6):
#         month = today.replace(day=1) + timedelta(days=32 * i)
#         month = month.replace(day=1)
#         forecast_months.append(month.strftime('%b %Y'))
#
#         # Simple forecast based on pipeline
#         pipeline_value = Lead.objects.filter(
#             stage__in=['qualified', 'survey', 'quote', 'negotiation']
#         ).aggregate(total=Sum('estimated_value'))['total'] or 0
#
#         forecast_values.append(float(pipeline_value) * 0.3)  # 30% probability
#
#     # Top Performing Sales Executives
#     top_performers = User.objects.filter(
#         assigned_leads__stage='won'
#     ).annotate(
#         total_revenue=Sum('assigned_leads__estimated_value'),
#         deals_closed=Count('assigned_leads')
#     ).order_by('-total_revenue')[:5]
#
#     # Recent Activities
#     recent_activities = LeadActivity.objects.select_related('user', 'lead')[:10]
#
#     context = {
#         'total_leads': total_leads,
#         'new_leads_today': new_leads_today,
#         'conversion_rate': round(conversion_rate, 1),
#         'revenue_closed': revenue_closed,
#         'forecast_revenue': forecast_revenue,
#         'followups_due': followups_due,
#         'overdue_followups': overdue_followups,
#         'leads_growth': round(leads_growth, 1),
#         'revenue_growth': 12.5,  # Placeholder
#         'conversion_change': 2.3,  # Placeholder
#         'funnel_data': funnel_data,
#         'forecast_months': json.dumps(forecast_months),
#         'forecast_values': json.dumps(forecast_values),
#         'top_performers': top_performers,
#         'recent_activities': recent_activities,
#     }
#
#     return render(request, 'dashboard/dashboard.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.db import OperationalError
from datetime import timedelta
import json

from apps.leads.models import Lead, LeadActivity, FollowUp
from django.contrib.auth.models import User

from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import default_storage
from .forms import (
    Step1BusinessForm, Step2AddressForm, Step3ContactForm,
    Step4BrandingForm, Step5AdminForm
)
from .models import Organization, UserProfile
from .utils import generate_unique_subdomain

FORMS = [
    ('business', Step1BusinessForm),
    ('address', Step2AddressForm),
    ('contact', Step3ContactForm),
    ('branding', Step4BrandingForm),
    ('admin', Step5AdminForm),
]

TEMPLATES = {
    'business': 'registration/step1.html',
    'address': 'registration/step2.html',
    'contact': 'registration/step3.html',
    'branding': 'registration/step4.html',
    'admin': 'registration/step5.html',
}


class OrganizationWizard(SessionWizardView):
    form_list = FORMS
    template_name = 'registration/wizard.html'
    file_storage = default_storage
    url_name = 'register'
    done_step_name = 'done'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.session_key:
            request.session.save()
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def render_done(self, form, **kwargs):
        """Override to handle missing session data after login."""
        try:
            return super().render_done(form, **kwargs)
        except KeyError:
            # Session data is gone, but we've already created the organization.
            messages.success(self.request, "Organization registered successfully! Welcome aboard.")
            return redirect('dashboard')

    def done(self, form_list, **kwargs):
        # ... your existing done method ...
        # Combine all cleaned data
        all_data = {}
        for form in form_list:
            all_data.update(form.cleaned_data)

        # Generate unique subdomain
        subdomain = generate_unique_subdomain(all_data['legal_name'])

        # Create Organization instance
        org = Organization(
            legal_name=all_data['legal_name'],
            trade_name=all_data.get('trade_name', ''),
            business_type=all_data['business_type'],
            industry=all_data.get('industry', ''),
            gst_number=all_data.get('gst_number', ''),
            pan_tax_id=all_data.get('pan_tax_id', ''),
            registration_number=all_data.get('registration_number', ''),
            address_line1=all_data['address_line1'],
            address_line2=all_data.get('address_line2', ''),
            city=all_data['city'],
            state=all_data['state'],
            country=all_data['country'],
            postal_code=all_data['postal_code'],
            official_email=all_data['official_email'],
            phone=all_data['phone'],
            alternate_phone=all_data.get('alternate_phone', ''),
            billing_email=all_data.get('billing_email', ''),
            website=all_data.get('website', ''),
            timezone=all_data['timezone'],
            currency=all_data['currency'],
            primary_color=all_data.get('primary_color', '#007bff'),
            secondary_color=all_data.get('secondary_color', '#6c757d'),
            subdomain=subdomain,
        )

        # Handle file uploads from the branding form
        branding_form = [f for f in form_list if isinstance(f, Step4BrandingForm)][0]
        if branding_form.cleaned_data.get('logo'):
            org.logo = branding_form.cleaned_data['logo']
        if branding_form.cleaned_data.get('digital_signature'):
            org.digital_signature = branding_form.cleaned_data['digital_signature']
        if branding_form.cleaned_data.get('company_stamp'):
            org.company_stamp = branding_form.cleaned_data['company_stamp']

        org.save()

        # Create admin user
        user = User.objects.create_user(
            username=all_data['admin_email'],
            email=all_data['admin_email'],
            password=all_data['password'],
            first_name=all_data['admin_full_name'],
        )
        # # Create profile
        # UserProfile.objects.create(
        #     user=user,
        #     organization=org,
        #     phone=all_data.get('admin_phone', ''),
        # )
        # Create profile and set is_tenant_admin = True
        profile = UserProfile.objects.create(
            user=user,
            organization=org,
            phone=all_data.get('admin_phone', ''),
        )
        profile.is_tenant_admin = True  # <-- Add this line
        profile.save()

        # ✅ Reset wizard storage before login to avoid session key loss
        try:
            self.storage.reset()
        except KeyError:
            # Already gone, ignore
            pass

        # Log the user in
        login(self.request, user)

        messages.success(self.request, "Organization registered successfully! Welcome aboard.")
        return redirect('dashboard')

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step = self.steps.current
        step_names = ['Business', 'Address', 'Contact', 'Branding', 'Admin']
        step_keys = [step[0] for step in FORMS]
        step_index = step_keys.index(current_step)
        context['progress'] = {
            'current': step_index + 1,
            'total': len(FORMS),
            'percent': int((step_index + 1) / len(FORMS) * 100),
            'step_names': step_names,
        }
        return context

# @login_required
# def dashboard(request):
#     """
#     Main dashboard view with all KPIs and charts
#     """
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#
#     # Initialize default values
#     context = {
#         'total_leads': 0,
#         'new_leads_today': 0,
#         'conversion_rate': 0,
#         'revenue_closed': 0,
#         'forecast_revenue': 0,
#         'followups_due': 0,
#         'overdue_followups': 0,
#         'leads_growth': 0,
#         'revenue_growth': 0,
#         'conversion_change': 0,
#         'funnel_data': {
#             'lead': 0,
#             'qualified': 0,
#             'survey': 0,
#             'quote': 0,
#             'won': 0,
#         },
#         'forecast_months': json.dumps([]),
#         'forecast_values': json.dumps([]),
#         'top_performers': [],
#         'recent_activities': [],
#     }
#
#     try:
#         # Check if tables exist before querying
#         if Lead.objects.exists():
#             # KPI Calculations
#             context['total_leads'] = Lead.objects.filter(created__date__gte=first_day_month).count()
#             context['new_leads_today'] = Lead.objects.filter(created__date=today).count()
#
#             # Conversion Rate
#             total_won = Lead.objects.filter(stage='won', created__date__gte=first_day_month).count()
#             total_qualified = Lead.objects.filter(created__date__gte=first_day_month).exclude(stage='new').count()
#             context['conversion_rate'] = round((total_won / total_qualified * 100), 1) if total_qualified > 0 else 0
#
#             # Revenue (simulated for now - will be replaced with actual revenue model)
#             revenue_closed_qs = Lead.objects.filter(
#                 stage='won',
#                 converted_at__date__gte=first_day_month
#             ).aggregate(total=Sum('estimated_value'))['total']
#             context['revenue_closed'] = revenue_closed_qs or 0
#
#             # Forecast Revenue (weighted pipeline)
#             leads_in_pipeline = Lead.objects.exclude(stage__in=['won', 'lost'])
#             context['forecast_revenue'] = sum(lead.weighted_value for lead in leads_in_pipeline)
#
#             # Lead heatmap data
#             leads_with_coords = Lead.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).values(
#                 'latitude', 'longitude')
#             heatmap_points = [[float(l['latitude']), float(l['longitude']), 1] for l in
#                               leads_with_coords]  # [lat, lng, intensity]
#             context['heatmap_points'] = json.dumps(heatmap_points)
#
#             # Growth calculations (compare with previous month)
#             last_month = first_day_month - timedelta(days=1)
#             last_month_first = last_month.replace(day=1)
#
#             last_month_leads = Lead.objects.filter(
#                 created__date__gte=last_month_first,
#                 created__date__lt=first_day_month
#             ).count()
#
#             context['leads_growth'] = round(((context['total_leads'] - last_month_leads) / last_month_leads * 100),
#                                             1) if last_month_leads > 0 else 0
#
#             # Pipeline Funnel Data
#             context['funnel_data'] = {
#                 'lead': Lead.objects.filter(stage='new').count(),
#                 'qualified': Lead.objects.filter(stage='qualified').count(),
#                 'survey': Lead.objects.filter(stage='survey').count(),
#                 'quote': Lead.objects.filter(stage='quote').count(),
#                 'won': Lead.objects.filter(stage='won').count(),
#             }
#
#             # Top Performing Sales Executives
#             context['top_performers'] = User.objects.filter(
#                 assigned_leads__stage='won'
#             ).annotate(
#                 total_revenue=Sum('assigned_leads__estimated_value'),
#                 deals_closed=Count('assigned_leads')
#             ).order_by('-total_revenue')[:5]
#
#         if FollowUp.objects.exists():
#             # Follow-ups
#             context['followups_due'] = FollowUp.objects.filter(
#                 scheduled_date__date=today,
#                 status='scheduled'
#             ).count()
#
#             context['overdue_followups'] = FollowUp.objects.filter(
#                 scheduled_date__date__lt=today,
#                 status='scheduled'
#             ).count()
#
#         if LeadActivity.objects.exists():
#             # Recent Activities
#             context['recent_activities'] = LeadActivity.objects.select_related('user', 'lead')[:10]
#
#         # Forecast Chart Data (next 6 months) - This doesn't depend on database
#         forecast_months = []
#         forecast_values = []
#         for i in range(6):
#             month = today.replace(day=1) + timedelta(days=32 * i)
#             month = month.replace(day=1)
#             forecast_months.append(month.strftime('%b %Y'))
#
#             # Simple forecast based on pipeline
#             pipeline_value = Lead.objects.filter(
#                 stage__in=['qualified', 'survey', 'quote', 'negotiation']
#             ).aggregate(total=Sum('estimated_value'))['total'] or 0
#
#             forecast_values.append(float(pipeline_value) * 0.3)  # 30% probability
#
#         context['forecast_months'] = json.dumps(forecast_months)
#         context['forecast_values'] = json.dumps(forecast_values)
#
#     except OperationalError:
#         # Tables don't exist yet - return default values
#         pass
#
#     return render(request, 'dashboard/dashboard.html', context)
#
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.db.models import Count, Sum, Avg
# from django.utils import timezone
# from django.db import OperationalError
# from datetime import timedelta
# import json
#
# from apps.leads.models import Lead, LeadActivity, FollowUp
# from django.contrib.auth.models import User
#
# @login_required
# def dashboard(request):
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#
#     # Initialize default values
#     context = {
#         'total_leads': 0,
#         'new_leads_today': 0,
#         'conversion_rate': 0,
#         'revenue_closed': 0,
#         'forecast_revenue': 0,
#         'followups_due': 0,
#         'overdue_followups': 0,
#         'leads_growth': 0,
#         'revenue_growth': 0,
#         'conversion_change': 0,
#         'funnel_data': {
#             'lead': 0,
#             'qualified': 0,
#             'survey': 0,
#             'quote': 0,
#             'won': 0,
#         },
#         'forecast_months': json.dumps([]),
#         'forecast_values': json.dumps([]),
#         'top_performers': [],
#         'recent_activities': [],
#         'heatmap_points': json.dumps([]),  # <-- new
#     }
#
#     try:
#         if Lead.objects.exists():
#             # KPI Calculations
#             context['total_leads'] = Lead.objects.filter(created__date__gte=first_day_month).count()
#             context['new_leads_today'] = Lead.objects.filter(created__date=today).count()
#
#             total_won = Lead.objects.filter(stage='won', created__date__gte=first_day_month).count()
#             total_qualified = Lead.objects.filter(created__date__gte=first_day_month).exclude(stage='new').count()
#             context['conversion_rate'] = round((total_won / total_qualified * 100), 1) if total_qualified > 0 else 0
#
#             revenue_closed_qs = Lead.objects.filter(
#                 stage='won',
#                 converted_at__date__gte=first_day_month
#             ).aggregate(total=Sum('estimated_value'))['total']
#             context['revenue_closed'] = revenue_closed_qs or 0
#
#             leads_in_pipeline = Lead.objects.exclude(stage__in=['won', 'lost'])
#             context['forecast_revenue'] = sum(lead.weighted_value for lead in leads_in_pipeline)
#
#             last_month = first_day_month - timedelta(days=1)
#             last_month_first = last_month.replace(day=1)
#             last_month_leads = Lead.objects.filter(
#                 created__date__gte=last_month_first,
#                 created__date__lt=first_day_month
#             ).count()
#             context['leads_growth'] = round(((context['total_leads'] - last_month_leads) / last_month_leads * 100), 1) if last_month_leads > 0 else 0
#
#             context['funnel_data'] = {
#                 'lead': Lead.objects.filter(stage='new').count(),
#                 'qualified': Lead.objects.filter(stage='qualified').count(),
#                 'survey': Lead.objects.filter(stage='survey').count(),
#                 'quote': Lead.objects.filter(stage='quote').count(),
#                 'won': Lead.objects.filter(stage='won').count(),
#             }
#
#             context['top_performers'] = User.objects.filter(
#                 assigned_leads__stage='won'
#             ).annotate(
#                 total_revenue=Sum('assigned_leads__estimated_value'),
#                 deals_closed=Count('assigned_leads')
#             ).order_by('-total_revenue')[:5]
#
#             # Heatmap: collect leads with coordinates
#             leads_with_coords = Lead.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
#             heatmap_points = []
#             for lead in leads_with_coords:
#                 heatmap_points.append([float(lead.latitude), float(lead.longitude), 1])  # intensity 1
#             context['heatmap_points'] = json.dumps(heatmap_points)
#
#         if FollowUp.objects.exists():
#             context['followups_due'] = FollowUp.objects.filter(
#                 scheduled_date__date=today,
#                 status='scheduled'
#             ).count()
#             context['overdue_followups'] = FollowUp.objects.filter(
#                 scheduled_date__date__lt=today,
#                 status='scheduled'
#             ).count()
#
#         if LeadActivity.objects.exists():
#             context['recent_activities'] = LeadActivity.objects.select_related('user', 'lead')[:10]
#
#         # Forecast Chart Data (next 6 months)
#         forecast_months = []
#         forecast_values = []
#         for i in range(6):
#             month = today.replace(day=1) + timedelta(days=32 * i)
#             month = month.replace(day=1)
#             forecast_months.append(month.strftime('%b %Y'))
#             pipeline_value = Lead.objects.filter(
#                 stage__in=['qualified', 'survey', 'quote', 'negotiation']
#             ).aggregate(total=Sum('estimated_value'))['total'] or 0
#             forecast_values.append(float(pipeline_value) * 0.3)
#         context['forecast_months'] = json.dumps(forecast_months)
#         context['forecast_values'] = json.dumps(forecast_values)
#
#     except OperationalError:
#         pass
#     return render(request, 'dashboard/dashboard.html', context)

#
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.db.models import Count, Sum, Avg, Q
# from django.utils import timezone
# from django.db import OperationalError
# from datetime import timedelta
# import json
#
# from apps.leads.models import Lead, LeadActivity, FollowUp
# from django.contrib.auth.models import User
#
# @login_required
# def dashboard(request):
#     today = timezone.now().date()
#     first_day_month = today.replace(day=1)
#
#     # Initialize default values
#     context = {
#         'total_leads': 0,
#         'new_leads_today': 0,
#         'conversion_rate': 0,
#         'revenue_closed': 0,
#         'forecast_revenue': 0,
#         'followups_due': 0,
#         'overdue_followups': 0,
#         'leads_growth': 0,
#         'revenue_growth': 0,
#         'conversion_change': 0,
#         'funnel_data': {
#             'lead': 0,
#             'qualified': 0,
#             'survey': 0,
#             'quote': 0,
#             'won': 0,
#         },
#         'forecast_months': json.dumps([]),
#         'forecast_values': json.dumps([]),
#         'top_performers': [],
#         'recent_activities': [],
#         'heatmap_points': json.dumps([]),
#     }
#
#     try:
#         if Lead.objects.exists():
#             # KPI Calculations
#             context['total_leads'] = Lead.objects.filter(created__date__gte=first_day_month).count()
#             context['new_leads_today'] = Lead.objects.filter(created__date=today).count()
#
#             total_won = Lead.objects.filter(stage='won', created__date__gte=first_day_month).count()
#             total_qualified = Lead.objects.filter(created__date__gte=first_day_month).exclude(stage='new').count()
#             context['conversion_rate'] = round((total_won / total_qualified * 100), 1) if total_qualified > 0 else 0
#
#             revenue_closed_qs = Lead.objects.filter(
#                 stage='won',
#                 converted_at__date__gte=first_day_month
#             ).aggregate(total=Sum('estimated_value'))['total']
#             context['revenue_closed'] = revenue_closed_qs or 0
#
#             leads_in_pipeline = Lead.objects.exclude(stage__in=['won', 'lost'])
#             context['forecast_revenue'] = sum(lead.weighted_value for lead in leads_in_pipeline)
#
#             last_month = first_day_month - timedelta(days=1)
#             last_month_first = last_month.replace(day=1)
#             last_month_leads = Lead.objects.filter(
#                 created__date__gte=last_month_first,
#                 created__date__lt=first_day_month
#             ).count()
#             context['leads_growth'] = round(((context['total_leads'] - last_month_leads) / last_month_leads * 100), 1) if last_month_leads > 0 else 0
#
#             context['funnel_data'] = {
#                 'lead': Lead.objects.filter(stage='new').count(),
#                 'qualified': Lead.objects.filter(stage='qualified').count(),
#                 'survey': Lead.objects.filter(stage='survey').count(),
#                 'quote': Lead.objects.filter(stage='quote').count(),
#                 'won': Lead.objects.filter(stage='won').count(),
#             }
#
#             context['top_performers'] = User.objects.filter(
#                 assigned_leads__stage='won'
#             ).annotate(
#                 total_revenue=Sum('assigned_leads__estimated_value'),
#                 deals_closed=Count('assigned_leads')
#             ).order_by('-total_revenue')[:5]
#
#             # Heatmap: collect leads with coordinates
#             leads_with_coords = Lead.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
#             heatmap_points = []
#             for lead in leads_with_coords:
#                 heatmap_points.append([float(lead.latitude), float(lead.longitude), 1])
#             context['heatmap_points'] = json.dumps(heatmap_points)
#
#         if FollowUp.objects.exists():
#             # Count scheduled follow‑ups due today
#             context['followups_due'] = FollowUp.objects.filter(
#                 scheduled_date__date=today,
#                 status='scheduled'
#             ).count()
#
#             # Overdue follow‑ups from FollowUp model
#             overdue_followups = FollowUp.objects.filter(
#                 scheduled_date__date__lt=today,
#                 status='scheduled'
#             ).count()
#
#             # Get IDs of leads that already have an overdue FollowUp (to avoid double‑counting)
#             leads_with_overdue_followups = FollowUp.objects.filter(
#                 scheduled_date__date__lt=today,
#                 status='scheduled'
#             ).values_list('lead_id', flat=True).distinct()
#
#             # Overdue leads that have next_followup in the past but no associated overdue FollowUp
#             overdue_from_leads = Lead.objects.filter(
#                 next_followup__date__lt=today
#             ).exclude(
#                 id__in=leads_with_overdue_followups
#             ).count()
#
#             # Overdue follow‑ups based on lead.next_followup (matches lead list)
#             context['overdue_followups'] = Lead.objects.filter(
#                 next_followup__date__lt=today
#             ).count()
#
#             # context['overdue_followups'] = overdue_followups + overdue_from_leads
#
#         if LeadActivity.objects.exists():
#             context['recent_activities'] = LeadActivity.objects.select_related('user', 'lead')[:10]
#
#         # Forecast Chart Data (next 6 months)
#         forecast_months = []
#         forecast_values = []
#         for i in range(6):
#             month = today.replace(day=1) + timedelta(days=32 * i)
#             month = month.replace(day=1)
#             forecast_months.append(month.strftime('%b %Y'))
#             pipeline_value = Lead.objects.filter(
#                 stage__in=['qualified', 'survey', 'quote', 'negotiation']
#             ).aggregate(total=Sum('estimated_value'))['total'] or 0
#             forecast_values.append(float(pipeline_value) * 0.3)
#         context['forecast_months'] = json.dumps(forecast_months)
#         context['forecast_values'] = json.dumps(forecast_values)
#
#     except OperationalError:
#         pass
#
#     return render(request, 'dashboard/dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.db import OperationalError
from datetime import timedelta
import json

from apps.leads.models import Lead, LeadActivity, FollowUp
from django.contrib.auth.models import User


def build_top_performers(request, limit=5):
    """
    Sales executives ranked by revenue on won deals — same rep set and revenue
    rules as the Sales Team page (team.views.sales_team_dashboard).
    """
    from decimal import Decimal
    from apps.revenue.models import Revenue
    from apps.team.views import _sales_team_rep_queryset

    revenue_filter = Q(payment_status__in=['paid', 'pending', 'partial'])
    rows = []

    for user in _sales_team_rep_queryset(request):
        user_leads = Lead.objects.filter(assigned_to=user)
        won_leads = user_leads.filter(stage='won')
        deals_closed = won_leads.count()
        if deals_closed == 0:
            continue

        total_revenue = Revenue.objects.filter(
            lead__assigned_to=user,
        ).filter(revenue_filter).aggregate(total=Sum('amount'))['total']

        if total_revenue:
            total_revenue = Decimal(str(total_revenue))
        else:
            total_revenue = won_leads.aggregate(total=Sum('estimated_value'))['total'] or Decimal('0')

        rows.append({
            'name': user.get_full_name() or user.username,
            'deals_closed': deals_closed,
            'total_revenue': total_revenue,
        })

    rows.sort(key=lambda row: (row['total_revenue'], row['deals_closed']), reverse=True)
    return rows[:limit]


def build_crm_dashboard_context(request):
    """Lead CRM dashboard metrics and chart data (shared by Main + CRM dashboards)."""
    from apps.core.utils import set_current_organization

    org = getattr(request, 'organization', None)
    if org:
        set_current_organization(org)

    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    last_month_end = first_day_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    context = {
        'total_leads': 0,
        'total_quotations': 0,
        'new_leads_month': 0,
        'new_leads_today': 0,
        'active_pipeline': 0,
        'conversion_rate': 0,
        'revenue_closed': 0,
        'forecast_revenue': 0,
        'followups_due': 0,
        'overdue_followups': 0,
        'leads_growth': 0,
        'revenue_growth': 0,
        'conversion_change': 0,
        'won_count': 0,
        'won_mtd': 0,
        'funnel_data': {
            'lead': 0,
            'qualified': 0,
            'survey': 0,
            'quote': 0,
            'won': 0,
        },
        'forecast_months': json.dumps([]),
        'forecast_values': json.dumps([]),
        'top_performers': [],
        'recent_activities': [],
        'heatmap_points': json.dumps([]),
    }

    try:
        from apps.revenue.models import Revenue
        from decimal import Decimal

        leads = Lead.objects.all()
        leads_mtd = leads.filter(created__date__gte=first_day_month)
        leads_prev_month = leads.filter(
            created__date__gte=last_month_start,
            created__date__lt=first_day_month,
        )

        context['total_leads'] = leads.count()
        from apps.quotations.views import crm_dashboard_total_quotations_count
        context['total_quotations'] = crm_dashboard_total_quotations_count(request.user)
        context['new_leads_month'] = leads_mtd.count()
        context['new_leads_today'] = leads.filter(created__date=today).count()
        context['active_pipeline'] = leads.exclude(stage__in=['won', 'lost']).count()
        context['won_count'] = leads.filter(stage='won').count()
        context['won_mtd'] = leads_mtd.filter(stage='won').count()

        new_mtd = context['new_leads_month']
        if new_mtd > 0:
            context['conversion_rate'] = round((context['won_mtd'] / new_mtd) * 100, 1)
        elif context['total_leads'] > 0:
            context['conversion_rate'] = round(
                (context['won_count'] / context['total_leads']) * 100, 1
            )

        revenue_paid = Revenue.objects.filter(
            payment_status='paid',
            date__gte=first_day_month,
        ).aggregate(total=Sum('amount'))['total']
        if revenue_paid:
            context['revenue_closed'] = revenue_paid
        else:
            context['revenue_closed'] = (
                leads.filter(stage='won').aggregate(total=Sum('estimated_value'))['total'] or 0
            )

        pipeline_leads = leads.exclude(stage__in=['won', 'lost'])
        forecast_total = Decimal('0')
        for lead in pipeline_leads.only('estimated_value', 'probability', 'stage'):
            forecast_total += lead.weighted_value or Decimal('0')
        context['forecast_revenue'] = forecast_total

        new_prev = leads_prev_month.count()
        context['leads_growth'] = (
            round(((new_mtd - new_prev) / new_prev) * 100, 1)
            if new_prev > 0
            else (100.0 if new_mtd > 0 else 0)
        )

        won_prev = leads_prev_month.filter(stage='won').count()
        prev_mtd_conv = round((won_prev / new_prev) * 100, 1) if new_prev > 0 else 0
        context['conversion_change'] = round(context['conversion_rate'] - prev_mtd_conv, 1)

        prev_revenue = Revenue.objects.filter(
            payment_status='paid',
            date__gte=last_month_start,
            date__lt=first_day_month,
        ).aggregate(total=Sum('amount'))['total'] or 0
        if float(prev_revenue) > 0:
            context['revenue_growth'] = round(
                ((float(context['revenue_closed']) - float(prev_revenue)) / float(prev_revenue)) * 100,
                1,
            )
        elif context['revenue_closed'] and float(context['revenue_closed']) > 0:
            context['revenue_growth'] = 100.0

        context['funnel_data'] = {
            'lead': leads.filter(stage='new').count(),
            'qualified': leads.filter(stage='qualified').count(),
            'survey': leads.filter(stage='survey').count(),
            'quote': leads.filter(stage='quote').count(),
            'won': context['won_count'],
        }

        context['top_performers'] = build_top_performers(request)

        heatmap_points = []
        for lead in leads.exclude(latitude__isnull=True).exclude(longitude__isnull=True).only(
            'latitude', 'longitude'
        ):
            heatmap_points.append([float(lead.latitude), float(lead.longitude), 1])
        context['heatmap_points'] = json.dumps(heatmap_points)

        if FollowUp.objects.exists():
            # Count scheduled follow‑ups due today
            context['followups_due'] = FollowUp.objects.filter(
                scheduled_date__date=today,
                status='scheduled'
            ).count()

        # Overdue follow‑ups based on lead.next_followup (matches lead list)
        context['overdue_followups'] = Lead.objects.filter(
            next_followup__date__lt=today
        ).count()

        if LeadActivity.objects.exists():
            context['recent_activities'] = LeadActivity.objects.select_related('user', 'lead')[:10]

        # Forecast Chart Data (next 6 months)
        forecast_months = []
        forecast_values = []
        for i in range(6):
            month = today.replace(day=1) + timedelta(days=32 * i)
            month = month.replace(day=1)
            forecast_months.append(month.strftime('%b %Y'))
            pipeline_value = Lead.objects.filter(
                stage__in=['qualified', 'survey', 'quote', 'negotiation']
            ).aggregate(total=Sum('estimated_value'))['total'] or 0
            forecast_values.append(float(pipeline_value) * 0.3)
        context['forecast_months'] = json.dumps(forecast_months)
        context['forecast_values'] = json.dumps(forecast_values)

    except OperationalError:
        pass

    return context


@login_required
def main_project_dashboard(request):
    """
    Main Dashboard: same content/logic as /index/, inside Lead CRM shell (base.html scripts).
    """
    from customer.staff_access import is_associate_staff
    from dashboard.views import build_main_dashboard_context

    if is_associate_staff(request.user) and not request.user.is_superuser:
        return redirect('customer-view_all')
    return render(
        request,
        'dashboard/main_project_dashboard.html',
        build_main_dashboard_context(request),
    )


@login_required
def dashboard(request):
    """CRM Dashboard — leads KPIs, charts, and Lead CRM logic."""
    return render(request, 'dashboard/dashboard.html', build_crm_dashboard_context(request))