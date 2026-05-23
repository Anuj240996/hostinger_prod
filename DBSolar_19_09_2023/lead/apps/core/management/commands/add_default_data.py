from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Organization
from apps.leads.models import LeadSource, Campaign
from apps.pipeline.models import PipelineStage
from apps.settings.models import LostReason, ScoringRule

class Command(BaseCommand):
    help = 'Add default lead sources, campaigns, pipeline stages, lost reasons, and scoring rules for all existing organizations'

    def handle(self, *args, **options):
        organizations = Organization.objects.all()
        if not organizations.exists():
            self.stdout.write(self.style.WARNING("No organizations found."))
            return

        for org in organizations:
            self.stdout.write(f"Processing organization: {org.legal_name}")

            # 1. Lead Sources
            lead_sources = [
                "Website", "Facebook Ads", "Instagram Ads", "Google Ads",
                "WhatsApp", "JustDial", "IndiaMART", "Referral",
                "Direct Walk-in", "Call Center", "Other"
            ]
            for name in lead_sources:
                obj, created = LeadSource.objects.get_or_create(
                    organization=org,
                    name=name,
                    defaults={'cost_per_lead': 0, 'is_active': True}
                )
                if created:
                    self.stdout.write(f"  Created LeadSource: {name}")

            # 2. Campaigns (requires a source, e.g., "Website")
            default_source = LeadSource.objects.filter(organization=org, name="Website").first()
            if default_source:
                campaigns = [
                    "General Campaign", "Festive Offer Campaign", "Subsidy Awareness Campaign",
                    "Commercial Solar Campaign", "Residential Solar Campaign", "Referral Campaign"
                ]
                for name in campaigns:
                    obj, created = Campaign.objects.get_or_create(
                        organization=org,
                        name=name,
                        defaults={
                            'source': default_source,
                            'start_date': timezone.now().date(),
                            'end_date': timezone.now().date() + timedelta(days=365),
                            'budget': 0,
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f"  Created Campaign: {name}")
            else:
                self.stdout.write(self.style.WARNING("  Skipped campaigns: No 'Website' lead source found."))

            # 3. Pipeline Stages
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
                obj, created = PipelineStage.objects.get_or_create(
                    organization=org,
                    name=name,
                    defaults={'order': order, 'probability': prob, 'color': color, 'is_active': True}
                )
                if created:
                    self.stdout.write(f"  Created PipelineStage: {name}")

            # 4. Lost Reasons
            lost_reasons = [
                "Price Too High", "Chose Competitor", "No Budget", "Not Interested",
                "No Subsidy", "Technical Not Feasible", "Delayed Decision",
                "Wrong Lead", "Duplicate Lead", "Other"
            ]
            for order, name in enumerate(lost_reasons, start=1):
                obj, created = LostReason.objects.get_or_create(
                    organization=org,
                    name=name,
                    defaults={'order': order, 'is_active': True}
                )
                if created:
                    self.stdout.write(f"  Created LostReason: {name}")

            # 5. Scoring Rules
            scoring_rules = [
                ("electricity_bill", "gt", "5000", 20),
                ("electricity_bill", "gt", "10000", 30),
                ("property_type", "eq", "commercial", 25),
                ("property_type", "eq", "residential", 10),
                ("budget", "gt", "0", 15),
            ]
            for criteria, condition, value, points in scoring_rules:
                obj, created = ScoringRule.objects.get_or_create(
                    organization=org,
                    criteria=criteria,
                    condition=condition,
                    value=value,
                    defaults={'points': points, 'is_active': True}
                )
                if created:
                    self.stdout.write(f"  Created ScoringRule: {criteria} {condition} {value}")

            self.stdout.write(self.style.SUCCESS(f"Finished organization: {org.legal_name}"))

        self.stdout.write(self.style.SUCCESS("All default data added successfully."))