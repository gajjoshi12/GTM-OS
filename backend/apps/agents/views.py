from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.workspace import WorkspaceScopedMixin, get_workspace

from . import orchestrator
from .models import ActivityEvent, Agent, AgentRun, Command, Decision
from .registry import GROUPS
from .serializers import (ActivityEventSerializer, AgentRunSerializer, AgentSerializer, CommandSerializer,
                          DecisionSerializer)


class AgentViewSet(WorkspaceScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    filterset_fields = ("group", "status", "enabled")
    pagination_class = None

    def list(self, request, *args, **kwargs):
        orchestrator.ensure_agents(self.get_workspace())
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        agent = self.get_object()
        run = orchestrator.run_agent(self.get_workspace(), agent.key, request.data.get("input") or {}, trigger=AgentRun.Trigger.MANUAL)
        return Response(AgentRunSerializer(run).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def groups(self, request):
        return Response([{"key": k, "label": v} for k, v in GROUPS.items()])

    @action(detail=False, methods=["post"])
    def run_all(self, request):
        """Full closed-loop pass (spec section 4) - runs every enabled agent in order."""
        ws = self.get_workspace()
        orchestrator.ensure_agents(ws)
        runs = [orchestrator.run_agent(ws, a.key, {"task": "closed-loop pass"}, trigger=AgentRun.Trigger.CMO)
                for a in Agent.objects.filter(workspace=ws, enabled=True).order_by("id")]
        return Response(AgentRunSerializer(runs, many=True).data)


class AgentRunViewSet(WorkspaceScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AgentRun.objects.select_related("agent")
    serializer_class = AgentRunSerializer
    filterset_fields = ("agent", "status", "trigger", "mode")
    ordering = ("-created_at",)


class DecisionViewSet(WorkspaceScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Decision.objects.select_related("agent")
    serializer_class = DecisionSerializer
    filterset_fields = ("status", "category", "impact", "requires_approval", "agent")
    search_fields = ("title", "body")
    ordering = ("-created_at",)

    def _resolve(self, request, pk, verb):
        d = orchestrator.resolve_decision(self.get_object(), verb, request.user, request.data.get("message", ""))
        return Response(DecisionSerializer(d).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._resolve(request, pk, "approve")

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._resolve(request, pk, "reject")

    @action(detail=True, methods=["post"])
    def ask(self, request, pk=None):
        return self._resolve(request, pk, "ask")

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        return Response({
            "pending": qs.filter(status=Decision.Status.PENDING).count(),
            "approved": qs.filter(status=Decision.Status.APPROVED).count(),
            "executed": qs.filter(status=Decision.Status.EXECUTED).count(),
            "rejected": qs.filter(status=Decision.Status.REJECTED).count(),
            "by_category": list(qs.values("category").annotate(count=Count("id"))),
            "high_impact_pending": qs.filter(status=Decision.Status.PENDING, impact__in=["high", "critical"]).count(),
        })


class CommandViewSet(WorkspaceScopedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Command.objects.prefetch_related("runs__agent")
    serializer_class = CommandSerializer
    ordering = ("-created_at",)

    def create(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "text is required"}, status=400)
        cmd = orchestrator.interpret_command(self.get_workspace(), request.user, text)
        return Response(CommandSerializer(cmd).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def suggestions(self, request):
        return Response([
            "Find me 5,000 European companies that match our ICP and launch an outbound campaign.",
            "Generate 30 new ads for our best-performing campaign.",
            "Why did revenue fall this week?",
            "Find a new customer segment.",
            "Get me 50 enterprise meetings next month.",
            "Reallocate budget toward the lowest-CAC channel.",
            "What is Competitor A saying in their ads right now?",
        ])


class ActivityViewSet(WorkspaceScopedMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ActivityEvent.objects.select_related("agent")
    serializer_class = ActivityEventSerializer
    filterset_fields = ("kind", "agent")
    ordering = ("-created_at",)


class OrgChartView(APIView):
    """Agent hierarchy for the org-chart visual (AI CMO -> groups -> agents)."""

    def get(self, request):
        ws = get_workspace(request)
        orchestrator.ensure_agents(ws)
        agents = Agent.objects.filter(workspace=ws).annotate(
            pending=Count("decisions", filter=Q(decisions__status=Decision.Status.PENDING))
        )
        by_group: dict[str, list] = {}
        cmo = None
        for a in agents:
            payload = {**AgentSerializer(a).data, "pending_decisions": a.pending}
            if a.key == "cmo":
                cmo = payload
            else:
                by_group.setdefault(a.group, []).append(payload)
        return Response({
            "cmo": cmo,
            "groups": [{"key": k, "label": GROUPS.get(k, k), "agents": v} for k, v in by_group.items()],
        })
