from rest_framework.routers import DefaultRouter

from .views import TimeEntryViewSet, TimerViewSet

router = DefaultRouter()
router.register("timer", TimerViewSet, basename="timer")
router.register("time-entries", TimeEntryViewSet, basename="time-entry")
urlpatterns = router.urls
