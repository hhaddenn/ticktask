from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, StageViewSet, TaskViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")
router.register("stages", StageViewSet, basename="stage")
urlpatterns = router.urls
