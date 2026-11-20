from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from projects.models import Project, Stage, Task

from .models import TimeEntry, TimerInterval


# Shared setup only, no tests: if it had test_ methods, every subclass would run
# them again.
class TimesheetTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="testuser", password="test")
        cls.other_user = get_user_model().objects.create_user(
            username="otheruser", password="othertest"
        )
        cls.project_a = Project.objects.create(owner=cls.user, name="Project A")
        cls.stage_a = Stage.objects.create(project=cls.project_a, name="Stage A")
        cls.task_a = Task.objects.create(project=cls.project_a, stage=cls.stage_a, title="Task A")

    def _open_entry(self, owner):
        date = timezone.localdate()
        started_at = timezone.now()
        return TimeEntry.objects.create(
            owner=owner, task=self.task_a, date=date, started_at=started_at
        )


# Each rule is tested on both sides: what it must reject, and the similar cases it
# must still allow (a badly written condition could block too much).
# IntegrityError comes from Postgres and aborts the transaction, hence atomic().
class TimeEntryConstraintTests(TimesheetTestBase):
    def test_second_open_timer_for_same_owner_is_rejected(self):
        self._open_entry(self.user)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._open_entry(self.user)

    def test_open_timers_for_different_owners_are_allowed(self):
        self._open_entry(self.user)
        self._open_entry(self.other_user)
        self.assertEqual(TimeEntry.objects.count(), 2)

    # Guards the ended_at__isnull part of the condition: without it, a user could
    # only ever have one timer session.
    def test_new_timer_after_closing_previous_is_allowed(self):
        entry = self._open_entry(self.user)
        entry.ended_at = timezone.now()
        entry.save()
        self._open_entry(self.user)
        self.assertEqual(TimeEntry.objects.count(), 2)

    def test_manual_entries_do_not_count_as_open_timer(self):
        self._open_entry(self.user)
        TimeEntry.objects.create(
            owner=self.user,
            task=self.task_a,
            date=timezone.localdate(),
            source=TimeEntry.Source.MANUAL,
            minutes=30,
        )
        self.assertEqual(TimeEntry.objects.count(), 2)

    def test_entry_ended_before_started_is_rejected(self):
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimeEntry.objects.create(
                    owner=self.user,
                    task=self.task_a,
                    date=timezone.localdate(),
                    started_at=now,
                    ended_at=now - timedelta(hours=1),
                )

    def test_manual_entry_without_minutes_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimeEntry.objects.create(
                    owner=self.user,
                    task=self.task_a,
                    date=timezone.localdate(),
                    source=TimeEntry.Source.MANUAL,
                )

    def test_task_with_time_entries_cannot_be_deleted(self):
        self._open_entry(self.user)
        # No atomic() here: PROTECT is checked by Django in Python before any SQL
        # runs, so the transaction is never broken.
        with self.assertRaises(ProtectedError):
            self.task_a.delete()


class TimerIntervalConstraintTests(TimesheetTestBase):
    def test_second_running_interval_in_same_entry_is_rejected(self):
        entry = self._open_entry(self.user)
        TimerInterval.objects.create(entry=entry, started_at=timezone.now())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimerInterval.objects.create(entry=entry, started_at=timezone.now())

    def test_closed_and_running_interval_in_same_entry_is_allowed(self):
        entry = self._open_entry(self.user)
        now = timezone.now()
        TimerInterval.objects.create(
            entry=entry, started_at=now - timedelta(hours=2), ended_at=now - timedelta(hours=1)
        )
        TimerInterval.objects.create(entry=entry, started_at=now)
        self.assertEqual(entry.intervals.count(), 2)

    def test_interval_ended_before_started_is_rejected(self):
        entry = self._open_entry(self.user)
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimerInterval.objects.create(
                    entry=entry, started_at=now, ended_at=now - timedelta(hours=1)
                )

    def test_deleting_entry_deletes_its_intervals(self):
        entry = self._open_entry(self.user)
        now = timezone.now()
        TimerInterval.objects.create(
            entry=entry, started_at=now - timedelta(hours=2), ended_at=now - timedelta(hours=1)
        )
        entry.delete()
        self.assertEqual(TimerInterval.objects.count(), 0)
