from django.db.models import Avg, Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.agents import orchestrator
from apps.core.workspace import WorkspaceScopedMixin

from .models import ICP, Company, Contact
from .serializers import CompanyDetailSerializer, CompanySerializer, ContactSerializer, ICPSerializer


class ICPViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = ICP.objects.all()
    serializer_class = ICPSerializer
    pagination_class = None

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        icp = self.get_object()
        icp.status = ICP.Status.APPROVED
        icp.save(update_fields=["status"])
        return Response(ICPSerializer(icp).data)

    @action(detail=False, methods=["post"])
    def derive(self, request):
        run = orchestrator.run_agent(self.get_workspace(), "icp", {"task": "derive ICPs"})
        return Response({"run_id": run.id, "summary": run.summary, "status": run.status})


class CompanyViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Company.objects.select_related("icp").annotate(contacts_count=Count("contacts"))
    serializer_class = CompanySerializer
    filterset_fields = ("tier", "icp", "country", "industry", "enriched", "source")
    search_fields = ("name", "domain", "industry", "country")
    ordering_fields = ("fit_score", "headcount", "revenue", "created_at")

    def get_serializer_class(self):
        return CompanyDetailSerializer if self.action == "retrieve" else CompanySerializer

    @action(detail=False, methods=["get"])
    def stats(self, request):
        # Deliberately NOT self.get_queryset(): that carries an annotate(Count("contacts"))
        # whose JOIN would multiply the per-tier counts by each company's contact count.
        qs = Company.objects.filter(workspace=self.get_workspace())
        return Response({
            "total": qs.count(),
            "by_tier": {str(r["tier"]): r["c"] for r in qs.values("tier").annotate(c=Count("id"))},
            "avg_fit": round(qs.aggregate(a=Avg("fit_score"))["a"] or 0, 1),
            "enriched": qs.filter(enriched=True).count(),
            "by_country": list(qs.values("country").annotate(c=Count("id")).order_by("-c")[:8]),
            "by_icp": list(qs.values("icp__name").annotate(c=Count("id")).order_by("-c")),
        })

    @action(detail=False, methods=["post"])
    def discover(self, request):
        ws = self.get_workspace()
        runs = [orchestrator.run_agent(ws, k, request.data or {}) for k in ("lead_discovery", "icp_scoring")]
        return Response([{"agent": r.agent.key, "summary": r.summary} for r in runs])


class ContactViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.select_related("company")
    serializer_class = ContactSerializer
    filterset_fields = ("company", "stage", "email_status", "persona", "seniority", "do_not_contact")
    search_fields = ("first_name", "last_name", "title", "email", "company__name")
    ordering_fields = ("lead_score", "created_at", "last_activity_at")

    @action(detail=False, methods=["get"])
    def funnel(self, request):
        qs = self.get_queryset()
        order = [s.value for s in Contact.Stage]
        counts = {r["stage"]: r["c"] for r in qs.values("stage").annotate(c=Count("id"))}
        return Response([{"stage": s, "count": counts.get(s, 0)} for s in order])

    @action(detail=False, methods=["post"])
    def enrich(self, request):
        ws = self.get_workspace()
        runs = [orchestrator.run_agent(ws, k) for k in ("lead_enrichment", "waterfall_data", "lead_verification")]
        return Response([{"agent": r.agent.key, "summary": r.summary} for r in runs])
