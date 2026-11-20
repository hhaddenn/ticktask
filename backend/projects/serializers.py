from django.db.models import Max
from rest_framework import serializers

from .models import Project, Stage, Task


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "archived_at", "created_at", "updated_at"]
        read_only_fields = ["archived_at", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        extra_kwargs = {"stage": {"required": False}}
        fields = [
            "id",
            "project",
            "stage",
            "title",
            "description",
            "sequence",
            "deadline_notified_at",
            "start_date",
            "due_date",
            "estimated_minutes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sequence", "deadline_notified_at", "created_at", "updated_at"]

    def validate_project(self, value):
        user = self.context["request"].user
        if value.owner_id != user.id:
            raise serializers.ValidationError("Project not found.")
        return value

    def validate(self, attrs):
        project = attrs.get("project")
        stage = attrs.get("stage")
        # Values the task will have after saving: on a partial PATCH, fields not sent
        # come from the saved task. Don't use `or` here: it would replace a null sent
        # on purpose (clearing the date) with the old value.
        start_date = attrs.get("start_date", self.instance.start_date if self.instance else None)
        due_date = attrs.get("due_date", self.instance.due_date if self.instance else None)
        if project and self.instance and project != self.instance.project:
            raise serializers.ValidationError({"project": "A task's project cannot be changed."})
        if stage and self.instance and stage != self.instance.stage:
            raise serializers.ValidationError({"stage": "Use the move action to change the stage."})
        if project and not stage and not project.stages.exists():
            raise serializers.ValidationError({"stage": "The project does not have any stages."})

        if project and stage:
            if stage.project_id != project.id:
                raise serializers.ValidationError(
                    {"stage": "Stage does not belong to the project."}
                )

        if start_date and due_date:
            if start_date > due_date:
                raise serializers.ValidationError(
                    {"due_date": "Due date cannot be before start date."}
                )
        return attrs

    def create(self, validated_data):
        project = validated_data["project"]
        stage = validated_data.get("stage")

        if stage is None:
            stage = project.stages.first()
            validated_data["stage"] = stage

        max_sequence = stage.tasks.aggregate(Max("sequence"))["sequence__max"]
        if max_sequence is None:
            validated_data["sequence"] = 0
        else:
            validated_data["sequence"] = max_sequence + 1
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "due_date" in validated_data and validated_data.get("due_date") != instance.due_date:
            validated_data["deadline_notified_at"] = None
        return super().update(instance, validated_data)


class TaskMoveSerializer(serializers.Serializer):
    stage = serializers.PrimaryKeyRelatedField(queryset=Stage.objects.all())
    position = serializers.IntegerField(min_value=0)


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ["id", "project", "name", "sequence", "is_done"]
