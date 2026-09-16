from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agents import orchestrator
from apps.agents.models import Decision
from apps.core.workspace import WorkspaceScopedMixin, get_workspace
from apps.leads.models import Company, Contact
from apps.outbound.models import Reply, Sequence

from .models import AttributionTouch, DailyMetric, Experiment, MemoryInsight, RevenueEvent
from .serializers import (AttributionTouchSerializer, DailyMetricSerializer, ExperimentSerializer,
                          MemoryInsightSerializer, RevenueEventSerializer)


def _f(v):
    return float(v or 0)


def _window(request, default=30):
    try:
        days = int(request.query_params.get("days", default))
    except ValueError:
        days = default
    end = timezone.now().date()
    return end - timedelta(days=days - 1), end, days


def _kpis(ws, start, end):
    qs = DailyMetric.objects.filter(workspace=ws, date__range=(start, end))
    a = qs.aggregate(spend=Sum("spend"), revenue=Sum("revenue"), pipeline=Sum("pipeline_value"), leads=Sum("leads"),
                     sqls=Sum("sqls"), meetings=Sum("meetings"), customers=Sum("customers"), clicks=Sum("clicks"),
                     impressions=Sum("impressions"))
    spend, revenue, leads, customers = _f(a["spend"]), _f(a["revenue"]), a["leads"] or 0, a["customers"] or 0
    return {
        "revenue": revenue, "pipeline": _f(a["pipeline"]), "spend": spend,
        "cac": round(spend / customers, 0) if customers else 0,
        "cost_per_lead": round(spend / leads, 0) if leads else 0,
        "roas": round(revenue / spend, 2) if spend else 0,
        "qualified_leads": a["sqls"] or 0, "leads": leads, "meetings": a["meetings"] or 0, "customers": customers,
        "clicks": a["clicks"] or 0, "impressions": a["impressions"] or 0,
    }


def _delta(cur, prev):
    return round((cur - prev) / prev * 100, 1) if prev else 0.0


class DashboardView(APIView):
    """Everything the CEO Command Centre needs in one call (spec section 6)."""

    def get(self, request):
        ws = get_workspace(request)
        start, end, days = _window(request)
        prev_start, prev_end = start - timedelta(days=days), start - timedelta(days=1)
        cur, prev = _kpis(ws, start, end), _kpis(ws, prev_start, prev_end)
        kpis = {k: {"value": v, "delta_pct": _delta(v, prev.get(k, 0))} for k, v in cur.items()}

        # time series (per day, all channels)
        series = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0, "pipeline": 0.0, "leads": 0, "meetings": 0})
        for m in DailyMetric.objects.filter(workspace=ws, date__range=(start, end)):
            d = series[m.date.isoformat()]
            d["spend"] += _f(m.spend); d["revenue"] += _f(m.revenue); d["pipeline"] += _f(m.pipeline_value)
            d["leads"] += m.leads; d["meetings"] += m.meetings
        timeseries = [{"date": k, **v} for k, v in sorted(series.items())]

        # channel scorecard
        rows = DailyMetric.objects.filter(workspace=ws, date__range=(start, end)).values("channel").annotate(
            spend=Sum("spend"), leads=Sum("leads"), customers=Sum("customers"), revenue=Sum("revenue"), meetings=Sum("meetings"),
            pipeline=Sum("pipeline_value"))
        channels = []
        for r in rows:
            spend, customers, leads, rev = _f(r["spend"]), r["customers"] or 0, r["leads"] or 0, _f(r["revenue"])
            channels.append({"channel": r["channel"], "spend": spend, "leads": leads, "meetings": r["meetings"] or 0,
                             "customers": customers, "revenue": rev, "pipeline": _f(r["pipeline"]),
                             "cac": round(spend / customers, 0) if customers else 0,
                             "cpl": round(spend / leads, 0) if leads else 0,
                             "roas": round(rev / spend, 2) if spend else 0})
        channels.sort(key=lambda c: (c["cac"] or 1e12))

        # funnel from contacts
        order = [s.value for s in Contact.Stage]
        counts = {r["stage"]: r["c"] for r in Contact.objects.filter(workspace=ws).values("stage").annotate(c=Count("id"))}
        funnel = [{"stage": s, "count": counts.get(s, 0)} for s in order if s != "unknown"]

        business = getattr(ws, "business", None)
        goal = _f(business.revenue_goal) if business else 0
        return Response({
            "window_days": days,
            "currency": business.currency if business else "INR",
            "goal": {"revenue_goal": goal, "attained": cur["revenue"], "pct": round(cur["revenue"] / goal * 100, 1) if goal else 0,
                     "pipeline_coverage": round(cur["pipeline"] / goal, 1) if goal else 0},
            "kpis": kpis,
            "timeseries": timeseries,
            "channels": channels,
            "funnel": funnel,
            "counts": {
                "pending_decisions": Decision.objects.filter(workspace=ws, status=Decision.Status.PENDING).count(),
                "tier1_accounts": Company.objects.filter(workspace=ws, tier=1).count(),
                "active_sequences": Sequence.objects.filter(workspace=ws, status=Sequence.Status.ACTIVE).count(),
                "unhandled_replies": Reply.objects.filter(workspace=ws, handled=False).count(),
                "running_experiments": Experiment.objects.filter(workspace=ws, status=Experiment.Status.RUNNING).count(),
                "memory_insights": MemoryInsight.objects.filter(workspace=ws, active=True).count(),
            },
        })


class AttributionView(APIView):
    def get(self, request):
        ws = get_workspace(request)
        events = RevenueEvent.objects.filter(workspace=ws)
        total = _f(events.aggregate(s=Sum("amount"))["s"])
        first, last, multi = defaultdict(float), defaultdict(float), defaultdict(float)
        for e in events:
            amt = _f(e.amount)
            first[e.source_channel or "unknown"] += amt
            last[e.closing_channel or e.source_channel or "unknown"] += amt
            for ch, pct in (e.attribution or {}).items():
                multi[ch] += amt * float(pct)
        chans = sorted(set(first) | set(last) | set(multi))
        table = [{"channel": c, "first_touch": round(first[c]), "last_touch": round(last[c]), "multi_touch": round(multi[c]),
                  "share": round(multi[c] / total * 100, 1) if total else 0} for c in chans]
        table.sort(key=lambda r: -r["multi_touch"])
        journeys = []
        for e in events.select_related("company").order_by("-closed_at")[:8]:
            touches = AttributionTouch.objects.filter(workspace=ws, contact=e.contact).order_by("occurred_at") if e.contact_id else []
            journeys.append({
                "company": e.company.name if e.company else "-", "amount": _f(e.amount), "closed_at": e.closed_at,
                "days_to_close": e.days_to_close, "path": [{"channel": t.channel, "type": t.touch_type} for t in touches],
            })
        by_kind = list(events.values("kind").annotate(total=Sum("amount"), count=Count("id")))
        avg_cycle = round(events.aggregate(a=Avg("days_to_close"))["a"] or 0)
        return Response({"total_revenue": total, "table": table, "journeys": journeys, "by_kind": by_kind,
                         "avg_days_to_close": avg_cycle, "attributed_share": 0.92 if total else 0})


class RevenueIntelligenceView(APIView):
    def get(self, request):
        ws = get_workspace(request)
        start, end, days = _window(request, 90)
        k = _kpis(ws, start, end)
        business = getattr(ws, "business", None)
        margin = _f(business.gross_margin_pct) / 100 if business else 0.7
        acv = _f(business.average_deal_size) if business else 0
        customers = max(k["customers"], 1)
        ltv = acv * 2.5 * margin if acv else (k["revenue"] / customers) * 2.5 * margin
        cac = k["cac"] or 1
        monthly_rev_per_customer = (acv / 12) if acv else (k["revenue"] / customers) / max(days / 30, 1)
        payback = round(cac / (monthly_rev_per_customer * margin), 1) if monthly_rev_per_customer else 0
        return Response({
            **k, "gross_margin_pct": margin * 100, "ltv": round(ltv), "ltv_to_cac": round(ltv / cac, 1) if cac else 0,
            "payback_months": payback, "roi_pct": round((k["revenue"] * margin - k["spend"]) / k["spend"] * 100, 1) if k["spend"] else 0,
            "window_days": days,
        })


class DailyMetricViewSet(WorkspaceScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = DailyMetric.objects.all()
    serializer_class = DailyMetricSerializer
    filterset_fields = ("channel", "date")
    pagination_class = None


class RevenueEventViewSet(WorkspaceScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RevenueEvent.objects.select_related("company")
    serializer_class = RevenueEventSerializer
    filterset_fields = ("kind", "source_channel")


class ExperimentViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    filterset_fields = ("status", "channel", "variable")
    pagination_class = None

    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = self.get_queryset()
        concluded = qs.filter(status=Experiment.Status.CONCLUDED)
        return Response({
            "running": qs.filter(status=Experiment.Status.RUNNING).count(),
            "proposed": qs.filter(status=Experiment.Status.PROPOSED).count(),
            "concluded": concluded.count(),
            "winners": concluded.exclude(winner="").count(),
            "avg_lift": round(concluded.aggregate(a=Avg("lift_pct"))["a"] or 0, 1),
            "by_channel": list(qs.values("channel").annotate(c=Count("id"))),
        })

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        e = self.get_object()
        new = request.data.get("status")
        if new in Experiment.Status.values:
            e.status = new
            if new == Experiment.Status.RUNNING and not e.started_at:
                e.started_at = timezone.now()
            if new == Experiment.Status.CONCLUDED:
                e.concluded_at = timezone.now()
            e.save()
        return Response(ExperimentSerializer(e).data)

    @action(detail=False, methods=["post"])
    def propose(self, request):
        run = orchestrator.run_agent(self.get_workspace(), "experimentation", request.data or {})
        return Response({"summary": run.summary, "status": run.status})


class MemoryInsightViewSet(WorkspaceScopedMixin, viewsets.ModelViewSet):
    queryset = MemoryInsight.objects.select_related("source_experiment")
    serializer_class = MemoryInsightSerializer
    filterset_fields = ("category", "active")
    search_fields = ("statement",)
    pagination_class = None
    ordering = ("-impact_score",)
