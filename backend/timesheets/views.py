from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import TimeEntrySerializer, TimerStartSerializer, TimerStopSerializer
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
