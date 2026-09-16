from __future__ import annotations

from django.db import models

from apps.core.workspace import WorkspaceModel


class Sequence(WorkspaceModel):
    """Multi-touch cadence built by the AI Sequence Agent (spec 2.9)."""

    class Status(models.TextChoices):
        DRAFT = "draft"
        PENDING_APPROVAL = "pending_approval"
        ACTIVE = "active"
        PAUSED = "paused"
        COMPLETED = "completed"

    class Channel(models.TextChoices):
        EMAIL = "email"
        LINKEDIN = "linkedin"
        MULTI = "multi"

    name = models.CharField(max_length=200)
    icp = models.ForeignKey("leads.ICP", null=True, blank=True, on_delete=models.SET_NULL, related_name="sequences")
    persona = models.CharField(max_length=80, blank=True)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    goal = models.CharField(max_length=200, blank=True)
    steps = models.JSONField(default=list, blank=True)  # [{day, channel, type, subject, body}]
    daily_cap = models.PositiveIntegerField(default=150)
    compliance_status = models.CharField(max_length=20, default="pending")  # pending | passed | flagged
    # rolled-up stats
    enrolled = models.PositiveIntegerField(default=0)
    sent = models.PositiveIntegerField(default=0)
    opened = models.PositiveIntegerField(default=0)
    replied = models.PositiveIntegerField(default=0)
    positive_replies = models.PositiveIntegerField(default=0)
    meetings = models.PositiveIntegerField(default=0)
    bounced = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def reply_rate(self):
        return round(self.replied / self.sent * 100, 1) if self.sent else 0.0


class Enrollment(WorkspaceModel):
    class Status(models.TextChoices):
        ACTIVE = "active"
        PAUSED = "paused"
        REPLIED = "replied"
        COMPLETED = "completed"
        UNSUBSCRIBED = "unsubscribed"

    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE, related_name="enrollments")
    contact = models.ForeignKey("leads.Contact", on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=14, choices=Status.choices, default=Status.ACTIVE)
    current_step = models.PositiveSmallIntegerField(default=0)
    next_send_at = models.DateTimeField(null=True, blank=True)
    personalization = models.JSONField(default=dict, blank=True)

    class Meta(WorkspaceModel.Meta):
        unique_together = ("sequence", "contact")


class OutboundMessage(WorkspaceModel):
    class Status(models.TextChoices):
        DRAFTED = "drafted"
        QA_PASSED = "qa_passed"
        QA_FLAGGED = "qa_flagged"
        SCHEDULED = "scheduled"
        SENT = "sent"
        BOUNCED = "bounced"

    enrollment = models.ForeignKey(Enrollment, null=True, blank=True, on_delete=models.CASCADE, related_name="messages")
    contact = models.ForeignKey("leads.Contact", on_delete=models.CASCADE, related_name="outbound_messages")
    sequence = models.ForeignKey(Sequence, null=True, blank=True, on_delete=models.SET_NULL, related_name="messages")
    step_index = models.PositiveSmallIntegerField(default=0)
    channel = models.CharField(max_length=10, default="email")
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    personalization_hooks = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFTED)
    qa = models.JSONField(default=dict, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    provider_message_id = models.CharField(max_length=120, blank=True)


class Reply(WorkspaceModel):
    """Inbound reply classified by Reply Intelligence and handled by the AI SDR (spec 2.10)."""

    class Classification(models.TextChoices):
        INTERESTED = "interested"
        NOT_NOW = "not_now"
        WRONG_PERSON = "wrong_person"
        SEND_INFO = "send_info"
        PRICING = "pricing_request"
        MEETING = "meeting_request"
        OBJECTION = "objection"
        UNSUBSCRIBE = "unsubscribe"
        NEGATIVE = "negative"
        OOO = "out_of_office"

    contact = models.ForeignKey("leads.Contact", on_delete=models.CASCADE, related_name="replies")
    sequence = models.ForeignKey(Sequence, null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    body = models.TextField()
    classification = models.CharField(max_length=20, choices=Classification.choices, blank=True)
    confidence = models.FloatField(default=0)
    next_action = models.CharField(max_length=200, blank=True)
    sdr_response = models.TextField(blank=True)
    handled = models.BooleanField(default=False)
    meeting_booked_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField()

    class Meta(WorkspaceModel.Meta):
        ordering = ("-received_at",)
        verbose_name_plural = "replies"
