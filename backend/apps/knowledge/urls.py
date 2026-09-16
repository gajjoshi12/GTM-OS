from rest_framework.routers import DefaultRouter

from .views import CompetitorViewSet, KnowledgeEntityViewSet, MarketSignalViewSet

router = DefaultRouter()
router.register("entities", KnowledgeEntityViewSet, basename="entity")
router.register("competitors", CompetitorViewSet, basename="competitor")
router.register("signals", MarketSignalViewSet, basename="signal")
urlpatterns = router.urls
