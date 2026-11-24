from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import TimeEntry

# Fixed for now: becomes the user's rounding_minutes preference in task 25.
DEFAULT_ROUNDING_MINUTES = 15


class TimerStateError(Exception):
    pass


# Always rounds up, so no work is left out (timer.md rule 9): 10 min counts as
# 15, never 0. Works from seconds, not whole minutes, so 15 min 30 s becomes 30
# instead of being truncated to 15 first. Sub-second leftovers are dropped.
def round_up_minutes(duration, block_minutes):
    total = int(duration.total_seconds())
    block_seconds = block_minutes * 60
    # Ceiling division with integers only (no float): floor of the negative, negated.
    total_blocks = -(-total // block_seconds)
    return total_blocks * block_minutes


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
    opened_entry.minutes = round_up_minutes(total, DEFAULT_ROUNDING_MINUTES)
    opened_entry.ended_at = now
    opened_entry.save()
    return opened_entry
