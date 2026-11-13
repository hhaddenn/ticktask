from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Stage
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        projects = self.request.user.projects.all()
        if self.action == "list":
            archived = self.request.query_params.get("archived") == "true"
            projects = projects.filter(archived_at__isnull=not archived)
        return projects

    def perform_create(self, serializer):
        with transaction.atomic():
            project = serializer.save(owner=self.request.user)
            Stage.objects.bulk_create(
                [
                    Stage(project=project, name="To Do", sequence=0),
                    Stage(project=project, name="In Progress", sequence=1),
                    Stage(project=project, name="Done", sequence=2, is_done=True),
                ]
            )

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        project = self.get_object()
        project.archived_at = timezone.now()
        project.save()
        return Response(self.get_serializer(project).data)

    @action(detail=True, methods=["post"])
    def unarchive(self, request, pk=None):
        project = self.get_object()
        project.archived_at = None
        project.save()
        return Response(self.get_serializer(project).data)
