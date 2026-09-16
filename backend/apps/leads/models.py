from __future__ import annotations

from django.db import models

from apps.core.workspace import WorkspaceModel


class ICP(WorkspaceModel):
    """Ideal Customer Profile derived from data (spec 2.4)."""

    class Status(models.TextChoices):
        DRAFT = "draft"
        APPROVED = "approved"
        PAUSED = "paused"

    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    rank = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    criteria = models.JSONField(default=dict, blank=True)  # industry, headcount, geo, tech, signals...
    personas = models.JSONField(default=list, blank=True)  # [{title, seniority, pain, message_angle}]
    buying_signals = models.JSONField(default=list, blank=True)
    expected_acv = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    estimated_tam = models.PositiveIntegerField(default=0)
    fit_summary = models.TextField(blank=True)
    # rolling performance
    prospects_count = models.PositiveIntegerField(default=0)
    reply_rate = models.FloatField(default=0)
    meeting_rate = models.FloatField(default=0)
    cac = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta(WorkspaceModel.Meta):
        ordering = ("rank", "id")

    def __str__(self):
        return self.name


class Company(WorkspaceModel):
    class Tier(models.IntegerChoices):
        T1 = 1, "Tier 1"
        T2 = 2, "Tier 2"
        T3 = 3, "Tier 3"

    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=160, blank=True)
    industry = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    headcount = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    funding_stage = models.CharField(max_length=60, blank=True)
    tech_stack = models.JSONField(default=list, blank=True)
    signals = models.JSONField(default=list, blank=True)  # hiring, expansion, modernization project...
    icp = models.ForeignKey(ICP, null=True, blank=True, on_delete=models.SET_NULL, related_name="companies")
    fit_score = models.PositiveSmallIntegerField(default=0)
    score_breakdown = models.JSONField(default=dict, blank=True)
    tier = models.PositiveSmallIntegerField(choices=Tier.choices, default=Tier.T3)
    source = models.CharField(max_length=60, blank=True)  # apollo | crm | csv | linkedin...
    enriched = models.BooleanField(default=False)
    linkedin_url = models.URLField(blank=True)
    logo_seed = models.CharField(max_length=60, blank=True)

    class Meta(WorkspaceModel.Meta):
        ordering = ("-fit_score", "id")
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Contact(WorkspaceModel):
    class EmailStatus(models.TextChoices):
        UNVERIFIED = "unverified"
        VALID = "valid"
        RISKY = "risky"
        INVALID = "invalid"

    class Stage(models.TextChoices):
        UNKNOWN = "unknown"
        VISITOR = "visitor"
        LEAD = "lead"
        MQL = "mql"
        SQL = "sql"
        OPPORTUNITY = "opportunity"
        CUSTOMER = "customer"
        REPEAT = "repeat"
        ADVOCATE = "advocate"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=160, blank=True)
    seniority = models.CharField(max_length=40, blank=True)
    persona = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    email_status = models.CharField(max_length=12, choices=EmailStatus.choices, default=EmailStatus.UNVERIFIED)
    phone = models.CharField(max_length=40, blank=True)
    linkedin_url = models.URLField(blank=True)
    stage = models.CharField(max_length=14, choices=Stage.choices, default=Stage.LEAD)
    lead_score = models.PositiveSmallIntegerField(default=0)
    do_not_contact = models.BooleanField(default=False)
    intelligence_card = models.JSONField(default=dict, blank=True, help_text="Prospect Intelligence Card (spec 2.8)")
    enrichment_log = models.JSONField(default=list, blank=True, help_text="Waterfall provider attempts")
    verification = models.JSONField(default=dict, blank=True)
    source = models.CharField(max_length=60, blank=True)
    owner = models.CharField(max_length=80, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name
