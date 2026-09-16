from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.agents import orchestrator
from apps.core.workspace import WorkspaceScopedMixin

from .models import BudgetAllocation, Campaign, Channel, ContentItem, Creative, LandingPage, SEOKeyword
from .serializers import (BudgetAllocationSerializer, CampaignDetailSerializer, CampaignSerializer, ContentItemSerializer,
                          CreativeSerializer, LandingPageSerializer, SEOKeywordSerializer)


class CampaignViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related("landing_page", "icp").annotate(creatives_count=Count("creatives"))
    serializer_class = CampaignSerializer
    filterset_fields = ("channel", "status", "objective", "managed_by_ai")
    search_fields = ("name",)
    pagination_class = None

    def get_serializer_class(self):
        return CampaignDetailSerializer if self.action == "retrieve" else CampaignSerializer

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        c = self.get_object()
        new = request.data.get("status")
        if new not in Campaign.Status.values:
            return Response({"detail": "invalid status"}, status=400)
        c.status = new
        c.save(update_fields=["status"])
        return Response(CampaignSerializer(c).data)

    @action(detail=False, methods=["get"])
    def channels(self, request):
        """Channel scorecard: spend, leads, CAC, ROAS - the Autonomous Media Buyer's inputs."""
        qs = self.get_queryset()
        rows = qs.values("channel").annotate(spend=Sum("total_spend"), leads=Sum("leads"), revenue=Sum("revenue"),
                                             pipeline=Sum("pipeline_value"), meetings=Sum("meetings"), budget=Sum("daily_budget"),
                                             campaigns=Count("id"))
        labels = dict(Channel.choices)
        out = []
        for r in rows:
            spend, leads, rev = float(r["spend"] or 0), r["leads"] or 0, float(r["revenue"] or 0)
            out.append({
                "channel": r["channel"], "label": labels.get(r["channel"], r["channel"]), "campaigns": r["campaigns"],
                "spend": spend, "leads": leads, "meetings": r["meetings"] or 0, "revenue": rev, "pipeline": float(r["pipeline"] or 0),
                "daily_budget": float(r["budget"] or 0), "cac": round(spend / leads, 0) if leads else 0,
                "roas": round(rev / spend, 2) if spend else 0,
            })
        return Response(sorted(out, key=lambda x: x["cac"] or 1e12))

    @action(detail=False, methods=["post"])
    def optimize(self, request):
        ws = self.get_workspace()
        runs = [orchestrator.run_agent(ws, k) for k in ("paid_media", "media_buyer", "creative_testing")]
        return Response([{"agent": r.agent.key, "summary": r.summary} for r in runs])


class CreativeViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Creative.objects.select_related("campaign")
    serializer_class = CreativeSerializer
    filterset_fields = ("campaign", "kind", "compliance_status", "is_winner", "active")
    pagination_class = None

    @action(detail=True, methods=["post"])
    def compliance(self, request, pk=None):
        c = self.get_object()
        status_ = request.data.get("status")
        if status_ in Creative.Compliance.values:
            c.compliance_status = status_
            c.save(update_fields=["compliance_status"])
        return Response(CreativeSerializer(c).data)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        ws = self.get_workspace()
        runs = [orchestrator.run_agent(ws, k, request.data or {}) for k in ("creative_director", "video", "compliance")]
        return Response([{"agent": r.agent.key, "summary": r.summary} for r in runs])


class BudgetAllocationViewSet(WorkspaceScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = BudgetAllocation.objects.all()
    serializer_class = BudgetAllocationSerializer
    filterset_fields = ("channel", "applied")
    ordering = ("-date", "-id")
    pagination_class = None


class LandingPageViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = LandingPage.objects.all()
    serializer_class = LandingPageSerializer
    filterset_fields = ("channel", "status")
    pagination_class = None


class ContentItemViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer
    filterset_fields = ("kind", "status", "theme", "platform")
    search_fields = ("title", "body")
    pagination_class = None

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        item = self.get_object()
        new = request.data.get("status")
        if new in ContentItem.Status.values:
            item.status = new
            item.save(update_fields=["status"])
        return Response(ContentItemSerializer(item).data)

    @action(detail=False, methods=["post"])
    def plan_week(self, request):
        ws = self.get_workspace()
        runs = [orchestrator.run_agent(ws, k) for k in ("content_strategy", "linkedin", "social", "seo", "brand_manager")]
        return Response([{"agent": r.agent.key, "summary": r.summary} for r in runs])


class SEOKeywordViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = SEOKeyword.objects.all()
    serializer_class = SEOKeywordSerializer
    filterset_fields = ("cluster", "intent", "status")
    pagination_class = None
