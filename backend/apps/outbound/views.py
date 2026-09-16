from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.agents import orchestrator
from apps.core.workspace import WorkspaceScopedMixin

from .models import Enrollment, OutboundMessage, Reply, Sequence
from .serializers import EnrollmentSerializer, OutboundMessageSerializer, ReplySerializer, SequenceSerializer


class SequenceViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Sequence.objects.select_related("icp")
    serializer_class = SequenceSerializer
    filterset_fields = ("status", "channel", "icp")
    search_fields = ("name", "persona")
    pagination_class = None

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        seq = self.get_object()
        new = request.data.get("status")
        if new not in Sequence.Status.values:
            return Response({"detail": "invalid status"}, status=400)
        seq.status = new
        seq.save(update_fields=["status"])
        return Response(SequenceSerializer(seq).data)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        ws = self.get_workspace()
        runs = [orchestrator.run_agent(ws, k, request.data or {}) for k in ("email_writer", "sequence", "compliance")]
        return Response([{"agent": r.agent.key, "summary": r.summary, "artifacts": r.output.get("artifacts", {})} for r in runs])

    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = self.get_queryset()
        agg = qs.aggregate(enrolled=Sum("enrolled"), sent=Sum("sent"), opened=Sum("opened"), replied=Sum("replied"),
                           positive=Sum("positive_replies"), meetings=Sum("meetings"), bounced=Sum("bounced"))
        agg = {k: v or 0 for k, v in agg.items()}
        agg["active"] = qs.filter(status=Sequence.Status.ACTIVE).count()
        agg["reply_rate"] = round(agg["replied"] / agg["sent"] * 100, 1) if agg["sent"] else 0
        agg["positive_rate"] = round(agg["positive"] / agg["sent"] * 100, 1) if agg["sent"] else 0
        agg["bounce_rate"] = round(agg["bounced"] / agg["sent"] * 100, 2) if agg["sent"] else 0
        return Response(agg)


class EnrollmentViewSet(WorkspaceScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Enrollment.objects.select_related("contact__company", "sequence")
    serializer_class = EnrollmentSerializer
    filterset_fields = ("sequence", "status")


class OutboundMessageViewSet(WorkspaceScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = OutboundMessage.objects.select_related("contact__company", "sequence")
    serializer_class = OutboundMessageSerializer
    filterset_fields = ("sequence", "status", "channel", "contact")
    search_fields = ("subject", "body", "contact__first_name", "contact__company__name")


class ReplyViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Reply.objects.select_related("contact__company", "sequence")
    serializer_class = ReplySerializer
    filterset_fields = ("classification", "handled", "sequence")
    search_fields = ("body", "contact__first_name", "contact__company__name")

    @action(detail=False, methods=["get"])
    def breakdown(self, request):
        qs = self.get_queryset()
        return Response({
            "total": qs.count(),
            "unhandled": qs.filter(handled=False).count(),
            "by_class": list(qs.values("classification").annotate(count=Count("id")).order_by("-count")),
            "meetings": qs.filter(meeting_booked_at__isnull=False).count(),
        })

    @action(detail=True, methods=["post"])
    def handle(self, request, pk=None):
        reply = self.get_object()
        reply.handled = True
        if request.data.get("sdr_response"):
            reply.sdr_response = request.data["sdr_response"]
        reply.save()
        return Response(ReplySerializer(reply).data)
