from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (AttributionView, DailyMetricViewSet, DashboardView, ExperimentViewSet, MemoryInsightViewSet,
                    RevenueEventViewSet, RevenueIntelligenceView)

router = DefaultRouter()
router.register("metrics", DailyMetricViewSet, basename="metric")
router.register("revenue-events", RevenueEventViewSet, basename="revenue-event")
router.register("experiments", ExperimentViewSet, basename="experiment")
router.register("memory", MemoryInsightViewSet, basename="memory")

urlpatterns = [
    path("dashboard/", DashboardView.as_view()),
    path("attribution/", AttributionView.as_view()),
    path("revenue-intelligence/", RevenueIntelligenceView.as_view()),
] + router.urls
