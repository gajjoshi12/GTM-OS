from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.workspace import WorkspaceScopedMixin

from .models import Competitor, KnowledgeEntity, MarketSignal
from .serializers import CompetitorSerializer, KnowledgeEntitySerializer, MarketSignalSerializer


class KnowledgeEntityViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = KnowledgeEntity.objects.prefetch_related("related")
    serializer_class = KnowledgeEntitySerializer
    filterset_fields = ("kind",)
    search_fields = ("name", "summary")
    pagination_class = None

    @action(detail=False, methods=["get"])
    def graph(self, request):
        """Nodes + edges for the knowledge-graph visual."""
        qs = self.get_queryset()
        nodes = [{"id": e.id, "kind": e.kind, "name": e.name, "confidence": e.confidence} for e in qs]
        edges, seen = [], set()
        for e in qs:
            for r in e.related.all():
                key = tuple(sorted((e.id, r.id)))
                if key not in seen:
                    seen.add(key)
                    edges.append({"source": key[0], "target": key[1]})
        coverage = list(qs.values("kind").annotate(count=Count("id")))
        return Response({"nodes": nodes, "edges": edges, "coverage": coverage})


class CompetitorViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    filterset_fields = ("threat_level",)
    search_fields = ("name", "positioning")
    pagination_class = None


class MarketSignalViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = MarketSignal.objects.all()
    serializer_class = MarketSignalSerializer
    filterset_fields = ("kind", "sentiment", "opportunity", "actioned")
    ordering = ("-detected_at",)
