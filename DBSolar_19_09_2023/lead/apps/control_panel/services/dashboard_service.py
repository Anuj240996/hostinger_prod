from datetime import date, timedelta
from django.db.models import Count, Sum, Q
from django.utils import timezone
from apps.core.models import Organization
from apps.leads.models import Lead
from apps.control_panel.models import OrganizationSubscription, SubscriptionPlan

def get_expiring_subscriptions(days=7):
    """Return queryset of active subscriptions expiring within next `days` days."""
    today = timezone.now().date()
    expiry_limit = today + timedelta(days=days)
    return OrganizationSubscription.objects.filter(
        status='active',
        end_date__gte=today,
        end_date__lte=expiry_limit
    ).select_related('organization', 'plan').order_by('end_date')

def get_expired_subscriptions():
    """Return queryset of subscriptions that have expired."""
    today = timezone.now().date()
    # Include both those marked 'expired' and active ones past expiry
    return OrganizationSubscription.objects.filter(
        Q(status='expired') | Q(end_date__lt=today, status='active')
    ).select_related('organization', 'plan').order_by('-end_date')

def get_platform_lead_stats():
    """Return aggregate lead statistics for owner dashboard."""
    today = timezone.now().date()
    leads_today = Lead.objects.filter(created__date=today).count()
    total_leads = Lead.objects.count()
    # Top 5 organizations by lead count
    top_orgs = Lead.objects.values('organization__legal_name').annotate(
        lead_count=Count('id')
    ).order_by('-lead_count')[:5]
    # Recently created leads (last 10)
    recent_leads = Lead.objects.select_related('organization').order_by('-created')[:10]
    return {
        'total_leads': total_leads,
        'leads_today': leads_today,
        'top_orgs': top_orgs,
        'recent_leads': recent_leads,
    }

def expire_subscriptions():
    today = timezone.now().date()
    expired = OrganizationSubscription.objects.filter(
        expiry_date__lt=today,
        status='active'
    )
    for sub in expired:
        sub.status = 'expired'
        sub.save()
        # Optionally suspend the organization
        # sub.organization.is_active = False
        # sub.organization.save()