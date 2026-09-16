from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ActivityViewSet, AgentRunViewSet, AgentViewSet, CommandViewSet, DecisionViewSet, OrgChartView

router = DefaultRouter()
router.register("agents", AgentViewSet, basename="agent")
router.register("runs", AgentRunViewSet, basename="agent-run")
router.register("decisions", DecisionViewSet, basename="decision")
router.register("commands", CommandViewSet, basename="command")
router.register("activity", ActivityViewSet, basename="activity")

urlpatterns = [path("org-chart/", OrgChartView.as_view())] + router.urls
