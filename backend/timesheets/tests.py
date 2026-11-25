from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import SimpleTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project, Stage, Task

from .models import TimeEntry, TimerInterval
from .services import (
    InvalidEndTimeError,
    TimerStateError,
    pause_timer,
    round_up_minutes,
    start_timer,
    stop_timer,
)


# Shared setup only, no tests: if it had test_ methods, every subclass would run
# them again.
class TimesheetTestBase(APITestCase):
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


class TimerApiTests(TimesheetTestBase):
    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def _post_at(self, url_name, when):
        with patch("django.utils.timezone.now", return_value=when):
            return self.client.post(reverse(url_name), {"task": self.task_a.id})

    def _get_at(self, when):
        with patch("django.utils.timezone.now", return_value=when):
            return self.client.get(reverse("timer-list"))

    def test_get_without_open_session_returns_no_content(self):
        response = self.client.get(reverse("timer-list"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_start_opens_running_session(self):
        response = self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state"], "running")
        self.assertEqual(response.data["task"], self.task_a.id)
        self.assertEqual(len(response.data["intervals"]), 1)
        self.assertIsNone(response.data["intervals"][0]["ended_at"])

    def test_pause_closes_running_interval(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-pause"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state"], "paused")
        self.assertEqual(len(response.data["intervals"]), 1)
        self.assertIsNotNone(response.data["intervals"][0]["ended_at"])

    def test_resume_opens_new_interval(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.client.post(reverse("timer-pause"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-resume"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state"], "running")
        self.assertEqual(len(response.data["intervals"]), 2)
        self.assertIsNone(response.data["intervals"][-1]["ended_at"])

    def test_stop_closes_session(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-stop"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state"], "stopped")
        self.assertIsNotNone(response.data["minutes"])
        response = self.client.get(reverse("timer-list"))
        self.assertIsNone(response.data)

    def test_stop_while_paused_closes_session(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.client.post(reverse("timer-pause"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-stop"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state"], "stopped")
        self.assertEqual(len(response.data["intervals"]), 1)

    def test_start_with_open_session_is_rejected(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(TimeEntry.objects.count(), 1)

    def test_pause_while_paused_is_rejected(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.client.post(reverse("timer-pause"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-pause"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_resume_while_running_is_rejected(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-resume"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(TimerInterval.objects.count(), 1)

    def test_start_with_other_users_task_is_rejected(self):
        new_project = Project.objects.create(owner=self.other_user, name="Project A")
        new_stage = Stage.objects.create(project=new_project, name="Stage A")
        new_task = Task.objects.create(project=new_project, stage=new_stage, title="Task A")
        response = self.client.post(reverse("timer-start"), {"task": new_task.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task", response.data)
        self.assertEqual(TimeEntry.objects.count(), 0)

    def test_start_on_archived_project_is_rejected(self):
        self.project_a.archived_at = timezone.now()
        self.project_a.save()
        response = self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task", response.data)
        self.assertEqual(TimeEntry.objects.count(), 0)

    def test_anonymous_user_is_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("timer-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stop_saves_rounded_minutes(self):
        t = datetime(2026, 11, 23, 9, 0, tzinfo=UTC)
        self._post_at(url_name="timer-start", when=t)
        self._post_at(url_name="timer-pause", when=t + timedelta(minutes=30))
        self._post_at(url_name="timer-resume", when=t + timedelta(minutes=60))
        response = self._post_at(url_name="timer-stop", when=t + timedelta(minutes=100))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["minutes"], 75)

    def test_stop_rounds_up_partial_minutes(self):
        t = datetime(2026, 11, 23, 9, 0, tzinfo=UTC)
        self._post_at(url_name="timer-start", when=t)
        response = self._post_at(url_name="timer-stop", when=t + timedelta(minutes=15, seconds=30))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["minutes"], 30)

    # 5 + 5 min worked gives 15. Rounding each interval on its own would give
    # 15 + 15 = 30 (timer.md rule 7: only the session total is rounded).
    def test_stop_rounds_session_total_not_each_interval(self):
        t = datetime(2026, 11, 23, 9, 0, tzinfo=UTC)
        self._post_at(url_name="timer-start", when=t)
        self._post_at(url_name="timer-pause", when=t + timedelta(minutes=5))
        self._post_at(url_name="timer-resume", when=t + timedelta(minutes=20))
        response = self._post_at(url_name="timer-stop", when=t + timedelta(minutes=25))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["minutes"], 15)

    def test_stop_keeps_exact_times_in_intervals(self):
        t = datetime(2026, 11, 23, 9, 0, tzinfo=UTC)
        self._post_at(url_name="timer-start", when=t)
        self._post_at(url_name="timer-stop", when=t + timedelta(minutes=15, seconds=30))
        entry = TimeEntry.objects.get(owner=self.user)
        total = sum((i.ended_at - i.started_at for i in entry.intervals.all()), timedelta())
        self.assertEqual(total, timedelta(minutes=15, seconds=30))
        self.assertEqual(entry.minutes, 30)

    def test_start_after_midnight_uses_lisbon_date(self):
        t = datetime(2026, 7, 15, 23, 30, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=t):
            response = self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["date"], "2026-07-16")

    def test_concurrent_start_is_rejected(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        with patch("timesheets.services.get_open_entry", return_value=None):
            response = self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(TimeEntry.objects.count(), 1)

    def test_open_session_includes_task_title_and_project_name(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        response = self.client.get(reverse("timer-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["task_title"], self.task_a.title)
        self.assertEqual(response.data["project_name"], self.project_a.name)

    def test_open_session_from_yesterday_is_forgotten(self):
        t = datetime(2026, 7, 15, 20, 30, tzinfo=UTC)
        self._post_at(url_name="timer-start", when=t)
        response = self._get_at(when=t + timedelta(days=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_forgotten"])

    def test_open_session_from_today_is_not_forgotten(self):
        t = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        self._post_at("timer-start", t)
        response = self._get_at(t + timedelta(hours=2))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_forgotten"])

    def test_stopped_session_is_not_forgotten(self):
        t = datetime(2026, 7, 15, 20, 30, tzinfo=UTC)
        self._post_at("timer-start", t)
        response = self._post_at("timer-stop", t + timedelta(days=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_forgotten"])

    # In July, 23:30 UTC is already 00:30 of the next day in Lisbon. Comparing with
    # the UTC date would still see "today" and miss the warning.
    def test_session_from_yesterday_is_forgotten_after_midnight_in_lisbon(self):
        started = datetime(2026, 7, 15, 20, 0, tzinfo=UTC)  # 21:00 on the 15th in Lisbon
        after_midnight = datetime(2026, 7, 15, 23, 30, tzinfo=UTC)  # 00:30 on the 16th in Lisbon
        self._post_at("timer-start", started)
        response = self._get_at(after_midnight)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_forgotten"])

    def test_stop_with_end_time_closes_session_at_that_time(self):
        started = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        self._post_at("timer-start", started)
        with patch("django.utils.timezone.now", return_value=started + timedelta(hours=3)):
            response = self.client.post(
                reverse("timer-stop"), {"ended_at": (started + timedelta(hours=1)).isoformat()}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["minutes"], 60)

    def test_stop_with_end_time_in_future_returns_400(self):
        started = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=started):
            self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        with patch("django.utils.timezone.now", return_value=started + timedelta(hours=3)):
            response = self.client.post(
                reverse("timer-stop"), {"ended_at": (started + timedelta(hours=4)).isoformat()}
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "The end time can't be in the future")

    def test_stop_with_malformed_end_time_returns_400(self):
        self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        response = self.client.post(reverse("timer-stop"), {"ended_at": "not-a-date"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)

    def test_stop_with_end_time_while_paused_returns_409(self):
        started = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=started):
            self.client.post(reverse("timer-start"), {"task": self.task_a.id})
        with patch("django.utils.timezone.now", return_value=started + timedelta(hours=1)):
            self.client.post(reverse("timer-pause"))
        with patch("django.utils.timezone.now", return_value=started + timedelta(hours=3)):
            response = self.client.post(
                reverse("timer-stop"),
                {"ended_at": (started + timedelta(hours=1, minutes=30)).isoformat()},
            )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["detail"], "The session is paused: stop it without an end time"
        )


class StopTimerServiceTests(TimesheetTestBase):
    def test_stop_with_end_time_closes_session_at_that_time(self):
        now = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=now):
            entry = start_timer(self.user, self.task_a)
        with patch("django.utils.timezone.now", return_value=now + timedelta(hours=3)):
            entry = stop_timer(self.user, ended_at=now + timedelta(hours=1))
        self.assertEqual(entry.ended_at, now + timedelta(hours=1))
        self.assertEqual(entry.intervals.get().ended_at, now + timedelta(hours=1))
        self.assertEqual(entry.minutes, 60)

    def test_stop_with_end_time_in_future_is_rejected(self):
        now = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=now):
            entry = start_timer(self.user, self.task_a)
        with patch("django.utils.timezone.now", return_value=now + timedelta(hours=3)):
            with self.assertRaises(InvalidEndTimeError):
                stop_timer(self.user, ended_at=now + timedelta(hours=4))
        entry.refresh_from_db()
        self.assertIsNone(entry.ended_at)

    def test_stop_with_end_time_before_interval_start_is_rejected(self):
        now = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=now):
            entry = start_timer(self.user, self.task_a)
        with patch("django.utils.timezone.now", return_value=now + timedelta(hours=3)):
            with self.assertRaises(InvalidEndTimeError):
                stop_timer(self.user, ended_at=now - timedelta(hours=1))
        entry.refresh_from_db()
        self.assertIsNone(entry.ended_at)

    def test_stop_with_end_time_while_paused_is_rejected(self):
        now = datetime(2026, 7, 15, 9, 0, tzinfo=UTC)
        with patch("django.utils.timezone.now", return_value=now):
            start_timer(self.user, self.task_a)
        with patch("django.utils.timezone.now", return_value=now + timedelta(hours=1)):
            pause_timer(self.user)
        with patch("django.utils.timezone.now", return_value=now + timedelta(hours=3)):
            with self.assertRaises(TimerStateError):
                stop_timer(self.user, ended_at=now + timedelta(hours=1, minutes=30))


class RoundUpMinutesTests(SimpleTestCase):
    def test_rounds_up_to_next_block(self):
        cases = [
            (timedelta(seconds=1), 15),
            (timedelta(minutes=10), 15),
            (timedelta(minutes=15, seconds=1), 30),
        ]
        for duration, expected in cases:
            with self.subTest(duration=duration):
                self.assertEqual(round_up_minutes(duration, 15), expected)

    def test_exact_multiple_is_not_rounded(self):
        cases = [(timedelta(minutes=15), 15), (timedelta(hours=1), 60)]
        for duration, expected in cases:
            with self.subTest(duration=duration):
                self.assertEqual(round_up_minutes(duration, 15), expected)

    def test_example_from_timer_doc(self):
        duration = timedelta(hours=7, minutes=7)
        expected = 435
        self.assertEqual(round_up_minutes(duration, 15), expected)

    def test_block_of_one_rounds_seconds_up(self):
        cases = [(timedelta(seconds=30), 1), (timedelta(minutes=10, seconds=1), 11)]
        for duration, expected in cases:
            with self.subTest(duration=duration):
                self.assertEqual(round_up_minutes(duration, 1), expected)

    def test_microseconds_are_ignored(self):
        duration = timedelta(minutes=15, milliseconds=300)
        expected = 15
        self.assertEqual(round_up_minutes(duration, 15), expected)

    def test_zero_duration_is_zero(self):
        duration = timedelta(seconds=0)
        expected = 0
        self.assertEqual(round_up_minutes(duration, 15), expected)
