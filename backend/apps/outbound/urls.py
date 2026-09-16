from rest_framework.routers import DefaultRouter

from .views import EnrollmentViewSet, OutboundMessageViewSet, ReplyViewSet, SequenceViewSet

router = DefaultRouter()
router.register("sequences", SequenceViewSet, basename="sequence")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("messages", OutboundMessageViewSet, basename="outbound-message")
router.register("replies", ReplyViewSet, basename="reply")
urlpatterns = router.urls
