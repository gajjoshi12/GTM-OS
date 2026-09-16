from __future__ import annotations

from django.db import models

from apps.core.workspace import WorkspaceModel


class DailyMetric(WorkspaceModel):
    """Unified customer-journey layer (spec 2.18): one row per day per channel."""

    date = models.DateField()
    channel = models.CharField(max_length=20)
    spend = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    visitors = models.PositiveIntegerField(default=0)
    leads = models.PositiveIntegerField(default=0)
    mqls = models.PositiveIntegerField(default=0)
    sqls = models.PositiveIntegerField(default=0)
    meetings = models.PositiveIntegerField(default=0)
    opportunities = models.PositiveIntegerField(default=0)
    customers = models.PositiveIntegerField(default=0)
    pipeline_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta(WorkspaceModel.Meta):
        unique_together = ("workspace", "date", "channel")
        ordering = ("date",)


class AttributionTouch(WorkspaceModel):
    contact = models.ForeignKey("leads.Contact", on_delete=models.CASCADE, related_name="touches")
    channel = models.CharField(max_length=20)
    campaign = models.ForeignKey("campaigns.Campaign", null=True, blank=True, on_delete=models.SET_NULL)
    touch_type = models.CharField(max_length=40)  # ad_click, email_open, reply, page_view, meeting...
    occurred_at = models.DateTimeField()
    weight = models.FloatField(default=1.0)

    class Meta(WorkspaceModel.Meta):
        ordering = ("occurred_at",)


class RevenueEvent(WorkspaceModel):
    class Kind(models.TextChoices):
        NEW = "new"
        EXPANSION = "expansion"
        RENEWAL = "renewal"

    company = models.ForeignKey("leads.Company", null=True, blank=True, on_delete=models.SET_NULL, related_name="revenue_events")
    contact = models.ForeignKey("leads.Contact", null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.NEW)
    source_channel = models.CharField(max_length=20, blank=True)  # first-touch
    closing_channel = models.CharField(max_length=20, blank=True)  # last-touch
    attribution = models.JSONField(default=dict, blank=True)  # multi-touch split {channel: pct}
    closed_at = models.DateTimeField()
    days_to_close = models.PositiveIntegerField(default=0)

    class Meta(WorkspaceModel.Meta):
        ordering = ("-closed_at",)


class Experiment(WorkspaceModel):
    """Hypothesis -> Experiment -> Measurement -> Decision -> Learning (spec 2.19)."""

    class Status(models.TextChoices):
        PROPOSED = "proposed"
        RUNNING = "running"
        CONCLUDED = "concluded"
        ABANDONED = "abandoned"

    name = models.CharField(max_length=200)
    hypothesis = models.TextField()
    channel = models.CharField(max_length=20)
    variable = models.CharField(max_length=80)  # headline, hook, audience, CTA, offer, send time...
    variants = models.JSONField(default=list, blank=True)  # [{label, description, exposures, conversions}]
    primary_metric = models.CharField(max_length=60, default="conversion_rate")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PROPOSED)
    confidence = models.FloatField(default=0)
    winner = models.CharField(max_length=40, blank=True)
    lift_pct = models.FloatField(default=0)
    learning = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    concluded_at = models.DateTimeField(null=True, blank=True)
    owner_agent = models.CharField(max_length=60, blank=True)


class MemoryInsight(WorkspaceModel):
    """Marketing Memory (spec 2.20): durable, propagating institutional learning."""

    statement = models.TextField()
    category = models.CharField(max_length=40)  # messaging, audience, channel, creative, timing, offer
    confidence = models.FloatField(default=0.8)
    evidence = models.JSONField(default=list, blank=True)
    applies_to = models.JSONField(default=list, blank=True)  # channels / agents that consume it
    source_experiment = models.ForeignKey(Experiment, null=True, blank=True, on_delete=models.SET_NULL)
    times_applied = models.PositiveIntegerField(default=0)
    impact_score = models.FloatField(default=0)
    active = models.BooleanField(default=True)
