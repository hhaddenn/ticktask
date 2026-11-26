from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TimeEntry
from .serializers import (
    TimeEntryRecordSerializer,
    TimeEntrySerializer,
    TimerStartSerializer,
    TimerStopSerializer,
)
from .services import (
    InvalidEndTimeError,
    TimerStateError,
    get_open_entry,
    pause_timer,
    resume_timer,
    start_timer,
    stop_timer,
)


class TimerViewSet(viewsets.ViewSet):
    def list(self, request):
        entry = get_open_entry(request.user)
        if entry:
            return Response(TimeEntrySerializer(entry).data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def start(self, request):
        serializer = TimerStartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        task = serializer.validated_data["task"]
        try:
            entry = start_timer(request.user, task)
            return Response(TimeEntrySerializer(entry).data)
        except TimerStateError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

    @action(detail=False, methods=["post"])
    def pause(self, request):
        try:
            entry = pause_timer(request.user)
            return Response(TimeEntrySerializer(entry).data)
        except TimerStateError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

    @action(detail=False, methods=["post"])
    def resume(self, request):
        try:
            entry = resume_timer(request.user)
            return Response(TimeEntrySerializer(entry).data)
        except TimerStateError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)

    @action(detail=False, methods=["post"])
    def stop(self, request):
        serializer = TimerStopSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        ended_at = serializer.validated_data.get("ended_at")
        try:
            entry = stop_timer(request.user, ended_at)
            return Response(TimeEntrySerializer(entry).data)
        except TimerStateError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        # 400 and not 409: the timer state allows a stop, only the end time sent is
        # wrong, so the same request with another time works (the UI shows it by the field).
        except InvalidEndTimeError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TimeEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimeEntryRecordSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        entries = self.request.user.time_entries.all()
        # The open timer session belongs to /api/timer/ (pause, resume, stop), so it's
        # left out here: editing or deleting it from this API gives a 404.
        entries = entries.exclude(source=TimeEntry.Source.TIMER, ended_at__isnull=True)
        task = self.request.query_params.get("task")
        if task and task.isdigit():
            entries = entries.filter(task__id=task)
        return entries

    def perform_create(self, serializer):
        # Always manual: timer sessions are only created by /api/timer/start/, with
        # intervals. A "timer" entry made here would have no exact times behind it.
        serializer.save(owner=self.request.user, source=TimeEntry.Source.MANUAL)
