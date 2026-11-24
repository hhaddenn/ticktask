from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from projects.models import Task

from .models import TimeEntry, TimerInterval


class TimerIntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimerInterval
        fields = ["id", "started_at", "ended_at"]


class TimeEntrySerializer(serializers.ModelSerializer):
    intervals = TimerIntervalSerializer(many=True, read_only=True)
    state = serializers.SerializerMethodField()
    elapsed_seconds = serializers.SerializerMethodField()
    task_title = serializers.CharField(source="task.title", read_only=True)
    project_name = serializers.CharField(source="task.project.name", read_only=True)

    def get_state(self, obj):
        if obj.ended_at is not None:
            return "stopped"
        intervals = obj.intervals.all()
        for interval in intervals:
            if interval.ended_at is None:
                return "running"
        return "paused"

    def get_elapsed_seconds(self, obj):
        intervals = obj.intervals.all()
        now = timezone.now()
        total = timedelta()
        for interval in intervals:
            total += (interval.ended_at or now) - interval.started_at
        return int(total.total_seconds())

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "task",
            "mode",
            "date",
            "started_at",
            "ended_at",
            "minutes",
            "description",
            "intervals",
            "state",
            "elapsed_seconds",
            "task_title",
            "project_name",
        ]
        read_only_fields = [
            "id",
            "task",
            "mode",
            "date",
            "started_at",
            "ended_at",
            "minutes",
            "description",
        ]


class TimerStartSerializer(serializers.Serializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        self.fields["task"].queryset = Task.objects.filter(project__owner=user)

    def validate_task(self, task):
        if task.project.archived_at is not None:
            raise serializers.ValidationError("The task's project is archived")
        return task
