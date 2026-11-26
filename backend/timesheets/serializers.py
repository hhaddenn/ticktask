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
    is_forgotten = serializers.SerializerMethodField()

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

    def get_is_forgotten(self, obj):
        ended_at = obj.ended_at
        date = obj.date
        if ended_at is None:
            # localdate(), not now().date(): date was saved with the Lisbon day on
            # start, and right after midnight in summer the UTC day is still yesterday.
            if date < timezone.localdate():
                return True
        return False

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
            "is_forgotten",
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


class TimerStopSerializer(serializers.Serializer):
    ended_at = serializers.DateTimeField(required=False)


class TimeEntryRecordSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.none())

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "task",
            "source",
            "date",
            "started_at",
            "ended_at",
            "minutes",
            "description",
        ]
        read_only_fields = ["id", "source", "started_at", "ended_at"]
        extra_kwargs = {"minutes": {"min_value": 1, "allow_null": False, "required": True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        self.fields["task"].queryset = Task.objects.filter(project__owner=user)

    def validate_task(self, task):
        if self.instance:
            if task != self.instance.task:
                raise serializers.ValidationError("Can't change the task of a time entry")
        # Only on create: an archived project's old hours must still be correctable,
        # so an update that sends the same task doesn't fail here.
        else:
            if task.project.archived_at is not None:
                raise serializers.ValidationError("The task's project is archived")
        return task

    def validate_date(self, date):
        # localdate(), not now().date(): same reason as in get_is_forgotten.
        if date > timezone.localdate():
            raise serializers.ValidationError("Date cannot be after today")
        return date

    def validate(self, attrs):
        # A timer session's date comes from its start and must match its intervals,
        # where the exact times live. Manual entries have no intervals, so theirs can change.
        if self.instance:
            if (
                self.instance.source == TimeEntry.Source.TIMER
                and "date" in attrs
                and attrs["date"] != self.instance.date
            ):
                raise serializers.ValidationError(
                    {"date": "Can't change the date of a timer session"}
                )
        return attrs
