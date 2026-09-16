from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.workspace import WorkspaceModel


class Agent(WorkspaceModel):
    """A specialist agent instance inside a workspace (spec section 1.4 / 2)."""

    class Status(models.TextChoices):
        IDLE = "idle"
        RUNNING = "running"
        PAUSED = "paused"
        ERROR = "error"

    key = models.SlugField(max_length=60)
    name = models.CharField(max_length=120)
    group = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    judged_on = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDLE)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    runs_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=1.0)
    health_score = models.PositiveSmallIntegerField(default=100)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_summary = models.CharField(max_length=300, blank=True)

    class Meta(WorkspaceModel.Meta):
        unique_together = ("workspace", "key")
        ordering = ("id",)

    def __str__(self):
        return f"{self.name} ({self.workspace_id})"


class AgentRun(WorkspaceModel):
    class Trigger(models.TextChoices):
        MANUAL = "manual"
        COMMAND = "command"
        CMO = "cmo"
        SCHEDULE = "schedule"
        EVENT = "event"

    class Status(models.TextChoices):
        QUEUED = "queued"
        RUNNING = "running"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="runs")
    trigger = models.CharField(max_length=20, choices=Trigger.choices, default=Trigger.MANUAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    input = models.JSONField(default=dict, blank=True)
    output = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    log = models.JSONField(default=list, blank=True)
    tokens_used = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=20, default="simulation")  # simulation | live
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(default=0)


class Decision(WorkspaceModel):
    """AI Decisions feed card (spec section 6) with Approve / Reject / Ask AI."""

    class Category(models.TextChoices):
        INSIGHT = "insight"
        OPPORTUNITY = "opportunity"
        ALERT = "alert"
        RECOMMENDATION = "recommendation"
        APPROVAL = "approval"

    class Impact(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
        EXECUTED = "executed"
        DISMISSED = "dismissed"

    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL, related_name="decisions")
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.RECOMMENDATION)
    impact = models.CharField(max_length=10, choices=Impact.choices, default=Impact.MEDIUM)
    confidence = models.FloatField(default=0.8)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requires_approval = models.BooleanField(default=True)
    action = models.JSONField(default=dict, blank=True, help_text="Machine-executable action payload")
    metrics = models.JSONField(default=dict, blank=True)
    conversation = models.JSONField(default=list, blank=True, help_text="Ask-AI thread")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class Command(WorkspaceModel):
    """Natural-language command bar entries interpreted by the AI CMO."""

    class Status(models.TextChoices):
        RECEIVED = "received"
        PLANNED = "planned"
        EXECUTING = "executing"
        DONE = "done"
        FAILED = "failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    text = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    intent = models.CharField(max_length=60, blank=True)
    plan = models.JSONField(default=dict, blank=True)
    response = models.TextField(blank=True)
    runs = models.ManyToManyField(AgentRun, blank=True, related_name="commands")


class ActivityEvent(WorkspaceModel):
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    kind = models.CharField(max_length=40)
    message = models.CharField(max_length=300)
    meta = models.JSONField(default=dict, blank=True)
