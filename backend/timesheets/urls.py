from rest_framework.routers import DefaultRouter

from .views import TimerViewSet

router = DefaultRouter()
router.register("timer", TimerViewSet, basename="timer")
urlpatterns = router.urls
