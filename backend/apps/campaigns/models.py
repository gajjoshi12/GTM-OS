from __future__ import annotations

from django.db import models

from apps.core.workspace import WorkspaceModel


class Channel(models.TextChoices):
    META = "meta", "Meta (FB + IG)"
    GOOGLE_SEARCH = "google_search", "Google Search"
    GOOGLE_DISPLAY = "google_display", "Google Display"
    YOUTUBE = "youtube", "YouTube"
    LINKEDIN = "linkedin", "LinkedIn Ads"
    TIKTOK = "tiktok", "TikTok Ads"
    X = "x", "X Ads"
    OUTBOUND = "outbound", "Outbound"
    ORGANIC = "organic", "Organic / SEO"


class LandingPage(WorkspaceModel):
    """Auto-generated, channel-matched page (spec 2.16)."""

    class Status(models.TextChoices):
        DRAFT = "draft"
        PENDING_APPROVAL = "pending_approval"
        LIVE = "live"
        ARCHIVED = "archived"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120)
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.GOOGLE_SEARCH)
    audience = models.CharField(max_length=160, blank=True)
    headline = models.CharField(max_length=200)
    subheadline = models.CharField(max_length=300, blank=True)
    cta = models.CharField(max_length=80, default="Book a demo")
    offer = models.CharField(max_length=200, blank=True)
    sections = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    visitors = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    active_experiment = models.CharField(max_length=200, blank=True)
    variants = models.JSONField(default=list, blank=True)

    @property
    def conversion_rate(self):
        return round(self.conversions / self.visitors * 100, 2) if self.visitors else 0.0

    def __str__(self):
        return self.name


class Campaign(WorkspaceModel):
    class Status(models.TextChoices):
        DRAFT = "draft"
        PENDING_APPROVAL = "pending_approval"
        ACTIVE = "active"
        PAUSED = "paused"
        ENDED = "ended"

    name = models.CharField(max_length=200)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    objective = models.CharField(max_length=60, default="lead_generation")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    icp = models.ForeignKey("leads.ICP", null=True, blank=True, on_delete=models.SET_NULL, related_name="campaigns")
    landing_page = models.ForeignKey(LandingPage, null=True, blank=True, on_delete=models.SET_NULL, related_name="campaigns")
    audience = models.JSONField(default=dict, blank=True)
    daily_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_spend = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    leads = models.PositiveIntegerField(default=0)
    meetings = models.PositiveIntegerField(default=0)
    pipeline_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    revenue = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    external_id = models.CharField(max_length=120, blank=True)
    managed_by_ai = models.BooleanField(default=True)
    started_at = models.DateTimeField(null=True, blank=True)

    @property
    def ctr(self):
        return round(self.clicks / self.impressions * 100, 2) if self.impressions else 0.0

    @property
    def cac(self):
        return round(float(self.total_spend) / self.leads, 2) if self.leads else 0.0

    @property
    def roas(self):
        return round(float(self.revenue) / float(self.total_spend), 2) if self.total_spend else 0.0

    def __str__(self):
        return self.name


class Creative(WorkspaceModel):
    """Ad variant produced by the Creative Director / Video Agent and tested (spec 2.14)."""

    class Kind(models.TextChoices):
        IMAGE = "image"
        VIDEO = "video"
        CAROUSEL = "carousel"
        TEXT = "text"

    class Compliance(models.TextChoices):
        PENDING = "pending"
        PASSED = "passed"
        FLAGGED = "flagged"
        REJECTED = "rejected"

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="creatives")
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.IMAGE)
    variant_label = models.CharField(max_length=20, default="A")
    hook = models.CharField(max_length=200, blank=True)
    headline = models.CharField(max_length=200)
    primary_text = models.TextField(blank=True)
    cta = models.CharField(max_length=60, default="Learn more")
    visual_direction = models.CharField(max_length=300, blank=True)
    asset_url = models.URLField(blank=True)
    gradient_seed = models.PositiveSmallIntegerField(default=1)
    audience_label = models.CharField(max_length=120, blank=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_winner = models.BooleanField(default=False)
    statistical_confidence = models.FloatField(default=0)
    compliance_status = models.CharField(max_length=10, choices=Compliance.choices, default=Compliance.PENDING)
    compliance_notes = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)

    @property
    def ctr(self):
        return round(self.clicks / self.impressions * 100, 2) if self.impressions else 0.0


class BudgetAllocation(WorkspaceModel):
    """A reallocation decision from the Autonomous Media Buyer (spec 2.15 / 2.19)."""

    date = models.DateField()
    channel = models.CharField(max_length=20, choices=Channel.choices)
    previous_daily = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_daily = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reason = models.TextField(blank=True)
    metrics = models.JSONField(default=dict, blank=True)  # cac, roas, ltv, margin, pipeline...
    decision = models.ForeignKey("agents.Decision", null=True, blank=True, on_delete=models.SET_NULL)
    applied = models.BooleanField(default=False)

    @property
    def delta_pct(self):
        return round((float(self.new_daily) - float(self.previous_daily)) / float(self.previous_daily) * 100, 1) if self.previous_daily else 0.0


class ContentItem(WorkspaceModel):
    """Rolling content calendar (spec 2.12 / 2.13)."""

    class Kind(models.TextChoices):
        LINKEDIN = "linkedin_post"
        BLOG = "blog"
        VIDEO = "video"
        INSTAGRAM = "instagram"
        X = "x_post"
        NEWSLETTER = "newsletter"
        CASE_STUDY = "case_study"
        YOUTUBE = "youtube"

    class Status(models.TextChoices):
        IDEA = "idea"
        DRAFTED = "drafted"
        PENDING_APPROVAL = "pending_approval"
        SCHEDULED = "scheduled"
        PUBLISHED = "published"

    title = models.CharField(max_length=220)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    theme = models.CharField(max_length=80, blank=True)  # industry insight, customer problem, case study...
    platform = models.CharField(max_length=30, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDEA)
    body = models.TextField(blank=True)
    hooks = models.JSONField(default=list, blank=True)
    hashtags = models.JSONField(default=list, blank=True)
    seo_keyword = models.CharField(max_length=120, blank=True)
    engagement = models.JSONField(default=dict, blank=True)  # impressions, likes, comments, clicks, leads
    compliance_status = models.CharField(max_length=10, default="pending")
    published_url = models.URLField(blank=True)

    class Meta(WorkspaceModel.Meta):
        ordering = ("scheduled_for", "id")


class SEOKeyword(WorkspaceModel):
    keyword = models.CharField(max_length=160)
    cluster = models.CharField(max_length=120, blank=True)
    intent = models.CharField(max_length=20, default="commercial")
    volume = models.PositiveIntegerField(default=0)
    difficulty = models.PositiveSmallIntegerField(default=0)
    current_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    previous_rank = models.PositiveSmallIntegerField(null=True, blank=True)
    target_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, default="tracking")

    class Meta(WorkspaceModel.Meta):
        ordering = ("-volume",)
