from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import TimeEntrySerializer, TimerStartSerializer
from .services import (
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
        try:
            entry = stop_timer(request.user)
            return Response(TimeEntrySerializer(entry).data)
        except TimerStateError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
