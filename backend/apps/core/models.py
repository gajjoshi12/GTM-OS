from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.accounts.models import Workspace


class BusinessProfile(models.Model):
    """The founder's one-sentence input + everything the system derives from it."""

    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, related_name="business")
    company_name = models.CharField(max_length=160)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    founder_brief = models.TextField(blank=True, help_text="Natural-language objective from the founder")
    currency = models.CharField(max_length=6, default=settings.DEFAULT_CURRENCY)
    revenue_goal = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    marketing_budget = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    gross_margin_pct = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    target_geographies = models.JSONField(default=list, blank=True)
    business_model = models.CharField(max_length=40, default="b2b_saas")
    average_deal_size = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sales_cycle_days = models.PositiveIntegerField(default=60)
    derived_plan = models.JSONField(default=dict, blank=True, help_text="AI CMO derivation: segments, personas, channels...")
    plan_generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name


class ControlSettings(models.Model):
    """Human Control Model (spec section 5)."""

    class Mode(models.TextChoices):
        COPILOT = "copilot", "Copilot - AI recommends, human executes"
        APPROVAL = "autonomous_with_approval", "Autonomous with approval"
        FULL = "full_autonomy", "Full autonomy within limits"

    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, related_name="controls")
    mode = models.CharField(max_length=40, choices=Mode.choices, default=settings.DEFAULT_CONTROL_MODE)
    daily_spend_cap = models.DecimalField(max_digits=14, decimal_places=2, default=settings.DEFAULT_DAILY_SPEND_CAP)
    monthly_spend_cap = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    max_daily_outbound = models.PositiveIntegerField(default=500)
    can_change_pricing = models.BooleanField(default=settings.AI_CAN_CHANGE_PRICING)
    can_email_unapproved_icps = models.BooleanField(default=settings.AI_CAN_EMAIL_UNAPPROVED_ICPS)
    can_launch_paid_without_approval = models.BooleanField(default=False)
    can_publish_social_without_approval = models.BooleanField(default=False)
    compliance_gate_required = models.BooleanField(default=settings.COMPLIANCE_GATE_REQUIRED)
    regulated_vertical = models.BooleanField(default=settings.REGULATED_VERTICAL)
    # per-agent overrides {"paid_media": "copilot", ...}
    agent_mode_overrides = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mode_for(self, agent_key: str) -> str:
        return self.agent_mode_overrides.get(agent_key, self.mode)


class BrandGuidelines(models.Model):
    """Enforced by the AI Brand Manager on every generated asset."""

    workspace = models.OneToOneField(Workspace, on_delete=models.CASCADE, related_name="brand")
    tone = models.CharField(max_length=200, default="Confident, precise, outcome-led. No hype.")
    voice_rules = models.JSONField(default=list, blank=True)
    vocabulary_preferred = models.JSONField(default=list, blank=True)
    vocabulary_banned = models.JSONField(default=list, blank=True)
    primary_color = models.CharField(max_length=9, default="#6d5dfc")
    secondary_color = models.CharField(max_length=9, default="#22d3ee")
    font_family = models.CharField(max_length=80, default="Inter")
    approved_claims = models.JSONField(default=list, blank=True)
    forbidden_claims = models.JSONField(default=list, blank=True)
    legal_disclaimer = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
