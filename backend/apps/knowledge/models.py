from __future__ import annotations

from django.db import models

from apps.core.workspace import WorkspaceModel


class KnowledgeEntity(WorkspaceModel):
    """Node in the Business Knowledge Graph (spec 2.1)."""

    class Kind(models.TextChoices):
        PRODUCT = "product"
        CUSTOMER = "customer"
        PROBLEM = "problem"
        SOLUTION = "solution"
        DIFFERENTIATOR = "differentiator"
        PRICING = "pricing"
        SALES_CYCLE = "sales_cycle"
        GEOGRAPHY = "geography"
        OBJECTION = "objection"
        USE_CASE = "use_case"
        OUTCOME = "outcome"
        PERSONA = "persona"

    kind = models.CharField(max_length=20, choices=Kind.choices)
    name = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    related = models.ManyToManyField("self", blank=True, symmetrical=True)
    source = models.CharField(max_length=120, blank=True)
    confidence = models.FloatField(default=0.8)
    freshness = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.kind}: {self.name}"


class Competitor(WorkspaceModel):
    class Threat(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    name = models.CharField(max_length=160)
    website = models.URLField(blank=True)
    positioning = models.TextField(blank=True)
    target_customer = models.CharField(max_length=200, blank=True)
    pricing = models.CharField(max_length=200, blank=True)
    usps = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    ad_messages = models.JSONField(default=list, blank=True, help_text="Observed ad creative / messaging patterns")
    seo_keywords = models.JSONField(default=list, blank=True)
    funding = models.CharField(max_length=120, blank=True)
    headcount = models.PositiveIntegerField(default=0)
    tech_stack = models.JSONField(default=list, blank=True)
    threat_level = models.CharField(max_length=10, choices=Threat.choices, default=Threat.MEDIUM)
    share_of_voice = models.FloatField(default=0)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class MarketSignal(WorkspaceModel):
    class Kind(models.TextChoices):
        NEWS = "news"
        FUNDING = "funding"
        HIRING = "hiring"
        LAUNCH = "launch"
        PRICING = "pricing"
        REGULATORY = "regulatory"
        TREND = "trend"
        COMPETITOR = "competitor"
        COMPLAINT = "complaint"

    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=240)
    summary = models.TextField(blank=True)
    entity = models.CharField(max_length=160, blank=True)
    source_url = models.URLField(blank=True)
    sentiment = models.CharField(max_length=12, default="neutral")  # positive | neutral | negative
    relevance = models.FloatField(default=0.5)
    opportunity = models.BooleanField(default=False)
    actioned = models.BooleanField(default=False)
    detected_at = models.DateTimeField()
