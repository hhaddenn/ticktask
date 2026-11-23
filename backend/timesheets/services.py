from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import TimeEntry


class TimerStateError(Exception):
    pass


def get_open_entry(user, lock=False):
    entry = TimeEntry.objects.filter(
        owner=user, source=TimeEntry.Source.TIMER, ended_at__isnull=True
    )
    if lock:
        entry = entry.select_for_update()
    return entry.first()


@transaction.atomic
def start_timer(user, task):
    opened_entry = get_open_entry(user, lock=True)
    now = timezone.now()
    if opened_entry is not None:
        raise TimerStateError("There is another session opened")
    try:
        with transaction.atomic():
            entry = TimeEntry.objects.create(
                owner=user, task=task, date=timezone.localdate(), started_at=now
            )
    except IntegrityError:
        raise TimerStateError("There is another session opened") from None
    entry.intervals.create(started_at=now)
    return entry


@transaction.atomic
def pause_timer(user):
    opened_entry = get_open_entry(user, lock=True)
    now = timezone.now()
    if opened_entry is None:
        raise TimerStateError("There is no opened session")
    interval = opened_entry.intervals.filter(ended_at__isnull=True).first()
    if interval is None:
        raise TimerStateError("Session already paused")
    interval.ended_at = now
    interval.save()
    return opened_entry


@transaction.atomic
def resume_timer(user):
    opened_entry = get_open_entry(user, lock=True)
    now = timezone.now()
    if opened_entry is None:
        raise TimerStateError("There is no opened session")
    if opened_entry.intervals.filter(ended_at__isnull=True).exists():
        raise TimerStateError("Timer is already running")
    try:
        with transaction.atomic():
            opened_entry.intervals.create(started_at=now)
    except IntegrityError:
        raise TimerStateError("There is no opened session") from None
    return opened_entry


@transaction.atomic
def stop_timer(user):
    opened_entry = get_open_entry(user, lock=True)
    now = timezone.now()
    if opened_entry is None:
        raise TimerStateError("There is no opened session")
    interval = opened_entry.intervals.filter(ended_at__isnull=True).first()
    if interval is not None:
        interval.ended_at = now
        interval.save()
    total = timedelta()
    for item in opened_entry.intervals.all():
        total += item.ended_at - item.started_at
    # Task 19 will change this for the rounding up
    opened_entry.minutes = int(total.total_seconds()) // 60
    opened_entry.ended_at = now
    opened_entry.save()
    return opened_entry
