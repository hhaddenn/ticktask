from django.conf import settings
from django.db import models
from django.db.models import F, Q


class TimeEntry(models.Model):
    class Source(models.TextChoices):
        TIMER = "timer"
        MANUAL = "manual"

    class Mode(models.TextChoices):
        NORMAL = "normal"
        POMODORO = "pomodoro"

    # Stored here, not only through task.project.owner, so the "one open timer per
    # user" constraint and the API filters can work on this table without joins.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="time_entries"
    )
    # Logged hours are history: deleting a task (or its project) must fail instead
    # of silently deleting them. Archive the project instead.
    task = models.ForeignKey("projects.Task", on_delete=models.PROTECT, related_name="time_entries")
    source = models.CharField(default=Source.TIMER, max_length=10, choices=Source)
    mode = models.CharField(default=Mode.NORMAL, max_length=10, choices=Mode)
    # No default on purpose: the timer API sets it on start with timezone.localdate(),
    # so a session started at 00:30 in Lisbon isn't filed under the previous (UTC) day.
    date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    # Pomodoro only: when the current break ends, so the countdown survives a page reload.
    break_ends_at = models.DateTimeField(null=True, blank=True)
    # Logged minutes. Timer: the session total rounded up on stop (exact times stay in
    # the intervals, timer.md rules 7-9). Manual entry: typed by the user.
    minutes = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task}, {self.date}"

    class Meta:
        # Manual entries have no started_at. Postgres puts NULLs first in a DESC
        # order, so without nulls_last they would jump ahead of the timer sessions.
        ordering = ["-date", F("started_at").desc(nulls_last=True)]
        # "timer" below is Source.TIMER (the class isn't reachable by name inside Meta).
        constraints = [
            # One open timer session per user (timer.md rule 2). Enforced by the
            # database, not only in the API: two requests at the same time (double
            # click on start, two tabs) could both see "no open timer" and both create one.
            models.UniqueConstraint(
                fields=["owner"],
                condition=Q(source="timer") & Q(ended_at__isnull=True),
                name="timeentry_one_open_timer_per_owner",
            ),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gt=F("started_at")),
                name="timeentry_ended_after_started",
            ),
            # A manual entry has no intervals, so minutes is the only place its time lives.
            models.CheckConstraint(
                condition=Q(source="timer") | Q(minutes__isnull=False),
                name="timeentry_manual_has_minutes",
            ),
        ]


class TimerInterval(models.Model):
    # CASCADE, unlike TimeEntry.task: an interval is only a part of its session,
    # not history on its own, so it goes away with the entry.
    entry = models.ForeignKey(TimeEntry, on_delete=models.CASCADE, related_name="intervals")
    started_at = models.DateTimeField()
    # NULL = running right now (pause and stop fill it in).
    ended_at = models.DateTimeField(null=True, blank=True)
    # Pomodoro only: the focus length. The interval never ends after
    # started_at + planned_minutes, even if the browser was closed (timer.md rule 15).
    planned_minutes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.started_at}, {self.ended_at}"

    class Meta:
        ordering = ["started_at"]
        constraints = [
            # One running interval per session. Together with the open-session rule on
            # TimeEntry, this gives "only one timer running per user".
            models.UniqueConstraint(
                fields=["entry"],
                condition=Q(ended_at__isnull=True),
                name="timerinterval_one_running_per_entry",
            ),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gt=F("started_at")),
                name="timerinterval_ended_after_started",
            ),
        ]
