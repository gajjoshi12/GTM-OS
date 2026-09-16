from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, ContactViewSet, ICPViewSet

router = DefaultRouter()
router.register("icps", ICPViewSet, basename="icp")
router.register("companies", CompanyViewSet, basename="company")
router.register("contacts", ContactViewSet, basename="contact")
urlpatterns = router.urls
