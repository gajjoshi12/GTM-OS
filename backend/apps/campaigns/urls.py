from rest_framework.routers import DefaultRouter

from .views import (BudgetAllocationViewSet, CampaignViewSet, ContentItemViewSet, CreativeViewSet, LandingPageViewSet,
                    SEOKeywordViewSet)

router = DefaultRouter()
router.register("campaigns", CampaignViewSet, basename="campaign")
router.register("creatives", CreativeViewSet, basename="creative")
router.register("allocations", BudgetAllocationViewSet, basename="allocation")
router.register("landing-pages", LandingPageViewSet, basename="landing-page")
router.register("content", ContentItemViewSet, basename="content")
router.register("seo-keywords", SEOKeywordViewSet, basename="seo-keyword")
urlpatterns = router.urls
