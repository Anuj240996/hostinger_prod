# import threading
#
# from django.template.defaultfilters import slugify
#
# from apps.core.models import Organization
#
# # from .models import Organization
#
# _thread_locals = threading.local()
#
# def set_current_organization(org):
#     """Store the current organization in thread-local storage."""
#     _thread_locals.organization = org
#
# def get_current_organization():
#     """Retrieve the current organization from thread-local storage."""
#     return getattr(_thread_locals, 'organization', None)
#
# def clear_current_organization():
#     """Clear the thread-local organization (useful for tests)."""
#     if hasattr(_thread_locals, 'organization'):
#         del _thread_locals.organization
#
# def generate_unique_subdomain(name):
#     """
#     Generate a unique subdomain from a business name.
#     """
#     base = slugify(name)[:50]  # slugify and truncate
#     if not base:
#         base = 'business'
#     unique = base
#     counter = 1
#     while Organization.objects.filter(subdomain=unique).exists():
#         unique = f"{base}{counter}"
#         counter += 1
#     return unique

import threading
from django.utils.text import slugify
from django.apps import apps

_thread_locals = threading.local()

def set_current_organization(org):
    """Store the current organization in thread-local storage."""
    _thread_locals.organization = org

def get_current_organization():
    """Retrieve the current organization from thread-local storage."""
    return getattr(_thread_locals, 'organization', None)

def clear_current_organization():
    """Clear the thread-local organization."""
    if hasattr(_thread_locals, 'organization'):
        del _thread_locals.organization

def generate_unique_subdomain(name):
    """
    Generate a unique subdomain from a business name.
    Uses apps.get_model to avoid circular imports.
    """
    Organization = apps.get_model('core', 'Organization')
    base = slugify(name)[:50]
    if not base:
        base = 'business'
    unique = base
    counter = 1
    while Organization.objects.filter(subdomain=unique).exists():
        unique = f"{base}{counter}"
        counter += 1
    return unique
#
# from django.utils import timezone
# from datetime import timedelta
#
# def add_default_data_for_organization(organization):
#     """Add default lead sources, campaigns, stages, lost reasons, and scoring rules for an organization."""
#     from apps.leads.models import LeadSource, Campaign
#     from apps.pipeline.models import PipelineStage
#     from apps.settings.models import LostReason, ScoringRule
#
#     # 1. Lead Sources
#     lead_sources = [
#         "Website", "Facebook Ads", "Instagram Ads", "Google Ads",
#         "WhatsApp", "JustDial", "IndiaMART", "Referral",
#         "Direct Walk-in", "Call Center", "Other"
#     ]
#     for name in lead_sources:
#         LeadSource.objects.get_or_create(
#             organization=organization,
#             name=name,
#             defaults={'cost_per_lead': 0, 'is_active': True}
#         )
#
#     # 2. Campaigns
#     campaigns = [
#         "General Campaign", "Festive Offer Campaign", "Subsidy Awareness Campaign",
#         "Commercial Solar Campaign", "Residential Solar Campaign", "Referral Campaign"
#     ]
#     # Get a default source (e.g., Website) to link campaigns
#     default_source = LeadSource.objects.filter(organization=organization, name="Website").first()
#     for name in campaigns:
#         Campaign.objects.get_or_create(
#             organization=organization,
#             name=name,
#             defaults={
#                 'source': default_source,
#                 'start_date': timezone.now().date(),
#                 'end_date': timezone.now().date() + timedelta(days=365),
#                 'budget': 0,
#                 'is_active': True
#             }
#         )
#
#     # 3. Lead Stages (Pipeline)
#     stages = [
#         ("New Lead", 10, "#0d6efd"),
#         ("Contacted", 20, "#6c757d"),
#         ("Qualified", 30, "#198754"),
#         ("Site Visit Scheduled", 40, "#0dcaf0"),
#         ("Survey Done", 50, "#ffc107"),
#         ("Quotation Sent", 60, "#fd7e14"),
#         ("Negotiation", 75, "#6f42c1"),
#         ("Token Paid", 90, "#20c997"),
#         ("Won", 100, "#198754"),
#         ("Lost", 0, "#dc3545"),
#     ]
#     for order, (name, prob, color) in enumerate(stages, start=1):
#         PipelineStage.objects.get_or_create(
#             organization=organization,
#             name=name,
#             defaults={'order': order, 'probability': prob, 'color': color, 'is_active': True}
#         )
#
#     # 4. Lost Reasons
#     lost_reasons = [
#         "Price Too High", "Chose Competitor", "No Budget", "Not Interested",
#         "No Subsidy", "Technical Not Feasible", "Delayed Decision",
#         "Wrong Lead", "Duplicate Lead", "Other"
#     ]
#     for order, name in enumerate(lost_reasons, start=1):
#         LostReason.objects.get_or_create(
#             organization=organization,
#             name=name,
#             defaults={'order': order, 'is_active': True}
#         )
#
#     # 5. Scoring Rules (adjust if you have additional fields like own_property, immediate_requirement)
#     scoring_rules = [
#         {"criteria": "electricity_bill", "condition": "gt", "value": "5000", "points": 20},
#         {"criteria": "electricity_bill", "condition": "gt", "value": "10000", "points": 30},
#         {"criteria": "property_type", "condition": "eq", "value": "commercial", "points": 25},
#         {"criteria": "property_type", "condition": "eq", "value": "residential", "points": 10},
#         {"criteria": "budget", "condition": "gt", "value": "0", "points": 15},
#         # If you have 'own_property' or 'immediate_requirement' fields in Lead model, add them:
#         # {"criteria": "own_property", "condition": "eq", "value": "True", "points": 20},
#         # {"criteria": "immediate_requirement", "condition": "eq", "value": "True", "points": 25},
#     ]
#     for rule in scoring_rules:
#         ScoringRule.objects.get_or_create(
#             organization=organization,
#             criteria=rule["criteria"],
#             condition=rule["condition"],
#             value=rule["value"],
#             defaults={'points': rule["points"], 'is_active': True}
#         )



from django.utils import timezone
from datetime import timedelta

def add_default_data_for_organization(organization):
    """Add default lead sources, campaigns, stages, lost reasons, and scoring rules for an organization."""
    from apps.leads.models import LeadSource, Campaign
    from apps.pipeline.models import PipelineStage
    from apps.settings.models import LostReason, ScoringRule

    # 1. Lead Sources (always created first)
    lead_sources = [
        "Website", "Facebook Ads", "Instagram Ads", "Google Ads",
        "WhatsApp", "JustDial", "IndiaMART", "Referral",
        "Direct Walk-in", "Call Center", "Other"
    ]
    for name in lead_sources:
        LeadSource.objects.get_or_create(
            organization=organization,
            name=name,
            defaults={'cost_per_lead': 0, 'is_active': True}
        )

    # 2. Campaigns – use the first available source (e.g., "Website")
    default_source = LeadSource.objects.filter(organization=organization).first()
    if default_source:
        campaigns = [
            "General Campaign", "Festive Offer Campaign", "Subsidy Awareness Campaign",
            "Commercial Solar Campaign", "Residential Solar Campaign", "Referral Campaign"
        ]
        for name in campaigns:
            Campaign.objects.get_or_create(
                organization=organization,
                name=name,
                defaults={
                    'source': default_source,
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timedelta(days=365),
                    'budget': 0,
                    'is_active': True
                }
            )
    else:
        # If no source exists (should not happen), skip campaign creation
        pass

    # 3. Lead Stages (Pipeline)
    stages = [
        ("New Lead", 10, "#0d6efd"),
        ("Contacted", 20, "#6c757d"),
        ("Qualified", 30, "#198754"),
        ("Site Visit Scheduled", 40, "#0dcaf0"),
        ("Survey Done", 50, "#ffc107"),
        ("Quotation Sent", 60, "#fd7e14"),
        ("Negotiation", 75, "#6f42c1"),
        ("Token Paid", 90, "#20c997"),
        ("Won", 100, "#198754"),
        ("Lost", 0, "#dc3545"),
    ]
    for order, (name, prob, color) in enumerate(stages, start=1):
        PipelineStage.objects.get_or_create(
            organization=organization,
            name=name,
            defaults={'order': order, 'probability': prob, 'color': color, 'is_active': True}
        )

    # 4. Lost Reasons
    lost_reasons = [
        "Price Too High", "Chose Competitor", "No Budget", "Not Interested",
        "No Subsidy", "Technical Not Feasible", "Delayed Decision",
        "Wrong Lead", "Duplicate Lead", "Other"
    ]
    for order, name in enumerate(lost_reasons, start=1):
        LostReason.objects.get_or_create(
            organization=organization,
            name=name,
            defaults={'order': order, 'is_active': True}
        )

    # 5. Scoring Rules
    scoring_rules = [
        ("electricity_bill", "gt", "5000", 20),
        ("electricity_bill", "gt", "10000", 30),
        ("property_type", "eq", "commercial", 25),
        ("property_type", "eq", "residential", 10),
        ("budget", "gt", "0", 15),
    ]
    for criteria, condition, value, points in scoring_rules:
        ScoringRule.objects.get_or_create(
            organization=organization,
            criteria=criteria,
            condition=condition,
            value=value,
            defaults={'points': points, 'is_active': True}
        )