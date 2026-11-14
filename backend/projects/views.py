from django.db import transaction
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Stage, Task
from .serializers import ProjectSerializer, StageSerializer, TaskMoveSerializer, TaskSerializer


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


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        tasks = Task.objects.filter(project__owner=self.request.user)
        project = self.request.query_params.get("project")
        if project and project.isdigit():
            tasks = tasks.filter(project__id=project)
        return tasks

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        task = self.get_object()
        serializer = TaskMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stage = serializer.validated_data["stage"]
        position = serializer.validated_data["position"]
        if stage.project_id != task.project_id:
            raise serializers.ValidationError(
                {"stage": "Cannot move a task to a stage from another project."}
            )
        with transaction.atomic():
            tasks = list(stage.tasks.exclude(pk=task.pk))
            tasks.insert(position, task)
            task.stage = stage
            for i, t in enumerate(tasks):
                t.sequence = i
            Task.objects.bulk_update(tasks, ["stage", "sequence"])
        return Response(self.get_serializer(task).data)


class StageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StageSerializer

    def get_queryset(self):
        stages = Stage.objects.filter(project__owner=self.request.user)
        project = self.request.query_params.get("project")
        if project and project.isdigit():
            stages = stages.filter(project__id=project)
        return stages
