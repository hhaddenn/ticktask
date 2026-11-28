from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from timesheets.models import TimeEntry

from .models import Project, Stage, Task


class TaskCleanTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="testuser", password="test")
        cls.project_a = Project.objects.create(owner=cls.user, name="Project A")
        cls.project_b = Project.objects.create(owner=cls.user, name="Project B")
        cls.stage_a = Stage.objects.create(project=cls.project_a, name="Stage A")
        cls.stage_b = Stage.objects.create(project=cls.project_b, name="Stage B")

    def test_stage_from_same_project_is_valid(self):
        task = Task(project=self.project_a, stage=self.stage_a, title="Task A")
        task.full_clean()

    def test_stage_from_other_project_is_invalid(self):
        task = Task(project=self.project_a, stage=self.stage_b, title="Task A")
        with self.assertRaises(ValidationError) as ctx:
            task.full_clean()
        self.assertIn("stage", ctx.exception.message_dict)

    def test_start_date_after_due_date_violates_constraint(self):
        with self.assertRaises(IntegrityError):
            # The IntegrityError aborts the current transaction; atomic() isolates it
            # so the rest of the test (and the next tests) can still use the database.
            with transaction.atomic():
                Task.objects.create(
                    project=self.project_a,
                    stage=self.stage_a,
                    title="Task A",
                    start_date=date(2026, 12, 10),
                    due_date=date(2026, 12, 1),
                )


class ProjectApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="userA", password="testA")
        cls.other_user = get_user_model().objects.create_user(username="userB", password="testB")
        cls.project_a = Project.objects.create(owner=cls.user, name="Project A")
        cls.project_b = Project.objects.create(owner=cls.other_user, name="Project B")

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_403_when_not_logged(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_only_shows_own_projects(self):
        response = self.client.get(reverse("project-list"))
        projects = [project["id"] for project in response.data]
        self.assertIn(self.project_a.id, projects)
        self.assertNotIn(self.project_b.id, projects)

    def test_other_users_project_returns_404(self):
        response = self.client.get(reverse("project-detail", args=[self.project_b.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_sets_owner_and_default_stages(self):
        response = self.client.post(
            reverse("project-list"), {"name": "New", "owner": self.other_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=response.data["id"])
        done_list = list(project.stages.values_list("is_done", flat=True))
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.stages.count(), 3)
        self.assertTrue(done_list[-1])

    def test_patch_updates_name(self):
        response = self.client.patch(
            reverse("project-detail", args=[self.project_a.id]), {"name": "Renamed"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project_a.refresh_from_db()
        self.assertEqual(self.project_a.name, "Renamed")

    def test_archive_hides_project_from_list(self):
        response = self.client.post(reverse("project-archive", args=[self.project_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project_a.refresh_from_db()
        self.assertIsNotNone(self.project_a.archived_at)
        response = self.client.get(reverse("project-list"))
        ids = [project["id"] for project in response.data]
        self.assertNotIn(self.project_a.id, ids)
        response = self.client.get(reverse("project-list"), {"archived": "true"})
        ids = [project["id"] for project in response.data]
        self.assertIn(self.project_a.id, ids)

    def test_unarchive_restores_project(self):
        self.project_a.archived_at = timezone.now()
        self.project_a.save(update_fields=["archived_at", "updated_at"])
        response = self.client.post(reverse("project-unarchive", args=[self.project_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project_a.refresh_from_db()
        self.assertIsNone(self.project_a.archived_at)

    def test_delete_not_allowed(self):
        response = self.client.delete(reverse("project-detail", args=[self.project_a.id]))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Project.objects.filter(id=self.project_a.id).exists())


class TaskApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="userA", password="testA")
        cls.other_user = get_user_model().objects.create_user(username="userB", password="testB")
        cls.project_a = Project.objects.create(owner=cls.user, name="Project A")
        cls.project_b = Project.objects.create(owner=cls.other_user, name="Project B")
        cls.stage_a = Stage.objects.create(project=cls.project_a, name="To Do", sequence=0)
        cls.stage_b = Stage.objects.create(project=cls.project_a, name="Doing", sequence=1)
        cls.stage_c = Stage.objects.create(project=cls.project_b, name="To Do", sequence=0)
        cls.task_a = Task.objects.create(
            project=cls.project_a, stage=cls.stage_a, title="Task A", sequence=0
        )
        cls.task_b = Task.objects.create(
            project=cls.project_a, stage=cls.stage_a, title="Task B", sequence=1
        )
        cls.task_c = Task.objects.create(project=cls.project_a, stage=cls.stage_b, title="Task C")
        cls.task_d = Task.objects.create(project=cls.project_b, stage=cls.stage_c, title="Task D")

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_list_only_shows_own_tasks(self):
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        id_list = [task["id"] for task in response.data]
        self.assertIn(self.task_a.id, id_list)
        self.assertNotIn(self.task_d.id, id_list)

    def test_list_filters_by_project(self):
        response = self.client.get(reverse("task-list"), {"project": self.project_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        id_list = [task["id"] for task in response.data]
        self.assertEqual(set(id_list), {self.task_a.id, self.task_b.id, self.task_c.id})

    def test_invalid_project_filter_is_ignored(self):
        response = self.client.get(reverse("task-list"), {"project": "abc"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        id_list = [task["id"] for task in response.data]
        self.assertIn(self.task_a.id, id_list)

    def test_other_users_task_returns_404(self):
        response = self.client.get(reverse("task-detail", args=[self.task_d.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_without_stage_uses_first_stage(self):
        response = self.client.post(
            reverse("task-list"), {"title": "Test", "project": self.project_a.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["stage"], self.stage_a.id)
        self.assertEqual(response.data["sequence"], 2)

    def test_create_in_empty_stage_starts_at_zero(self):
        empty_stage = Stage.objects.create(name="Test", project=self.project_a, sequence=2)
        response = self.client.post(
            reverse("task-list"),
            {"title": "Test", "project": self.project_a.id, "stage": empty_stage.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sequence"], 0)

    def test_create_with_stage_from_other_project_returns_400(self):
        response = self.client.post(
            reverse("task-list"),
            {"title": "Test", "project": self.project_a.id, "stage": self.stage_c.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stage", response.data)

    def test_create_in_other_users_project_returns_400(self):
        response = self.client.post(
            reverse("task-list"),
            {"title": "Test", "project": self.project_b.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project", response.data)

    def test_patch_updates_title(self):
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"title": "New Test"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.title, "New Test")

    def test_patch_cannot_change_project(self):
        project_c = Project.objects.create(owner=self.user, name="Project C")
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"project": project_c.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("project", response.data)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.project, self.project_a)

    def test_patch_cannot_change_stage(self):
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"stage": self.stage_b.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stage", response.data)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.stage, self.stage_a)

    def test_changing_due_date_clears_notification(self):
        self.task_a.deadline_notified_at = timezone.now()
        self.task_a.save()
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"due_date": "2026-12-01"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertIsNone(self.task_a.deadline_notified_at)

    def test_patch_without_due_date_keeps_notification(self):
        self.task_a.deadline_notified_at = timezone.now()
        self.task_a.save()
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"title": "New title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertIsNotNone(self.task_a.deadline_notified_at)

    def test_removing_due_date_clears_notification(self):
        self.task_a.deadline_notified_at = timezone.now()
        self.task_a.due_date = date(2026, 12, 1)
        self.task_a.save()
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"due_date": None}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertIsNone(self.task_a.deadline_notified_at)

    def test_patch_due_date_before_saved_start_date_returns_400(self):
        self.task_a.start_date = date(2026, 12, 10)
        self.task_a.save()
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"due_date": "2026-12-01"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("due_date", response.data)

    def test_patch_valid_dates_returns_200(self):
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]),
            {"start_date": "2026-12-01", "due_date": "2026-12-10"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.start_date, date(2026, 12, 1))
        self.assertEqual(self.task_a.due_date, date(2026, 12, 10))

    def test_patch_clearing_due_date_with_saved_start_date_returns_200(self):
        self.task_a.start_date = date(2026, 12, 1)
        self.task_a.due_date = date(2026, 12, 10)
        self.task_a.save()
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"due_date": None}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.start_date, date(2026, 12, 1))
        self.assertIsNone(self.task_a.due_date)

    def test_patch_new_start_date_and_cleared_due_date_returns_200(self):
        self.task_a.start_date = date(2026, 12, 1)
        self.task_a.due_date = date(2026, 12, 10)
        self.task_a.save()
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]),
            {"start_date": "2026-12-25", "due_date": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.start_date, date(2026, 12, 25))
        self.assertIsNone(self.task_a.due_date)

    def test_move_to_other_stage_at_top(self):
        response = self.client.post(
            reverse("task-move", args=[self.task_a.id]),
            {"stage": self.stage_b.id, "position": 0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stage_b_order = list(self.stage_b.tasks.values_list("id", flat=True))
        stage_a_order = list(self.stage_a.tasks.values_list("id", flat=True))
        self.assertEqual(stage_b_order, [self.task_a.id, self.task_c.id])
        self.assertEqual(stage_a_order, [self.task_b.id])
        self.assertEqual(response.data["stage"], self.stage_b.id)

    def test_move_within_same_stage(self):
        response = self.client.post(
            reverse("task-move", args=[self.task_a.id]),
            {"stage": self.stage_a.id, "position": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stage_a_order = list(self.stage_a.tasks.values_list("id", flat=True))
        self.assertEqual(stage_a_order, [self.task_b.id, self.task_a.id])
        self.task_a.refresh_from_db()
        self.task_b.refresh_from_db()
        self.assertEqual(self.task_b.sequence, 0)
        self.assertEqual(self.task_a.sequence, 1)

    def test_move_beyond_end_goes_last(self):
        response = self.client.post(
            reverse("task-move", args=[self.task_a.id]),
            {"stage": self.stage_b.id, "position": 99},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stage_b_order = list(self.stage_b.tasks.values_list("id", flat=True))
        self.assertEqual(stage_b_order, [self.task_c.id, self.task_a.id])

    def test_move_to_other_project_stage_returns_400(self):
        response = self.client.post(
            reverse("task-move", args=[self.task_a.id]),
            {"stage": self.stage_c.id, "position": 0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stage", response.data)
        self.task_a.refresh_from_db()
        self.assertEqual(self.task_a.stage, self.stage_a)

    def test_move_with_negative_position_returns_400(self):
        response = self.client.post(
            reverse("task-move", args=[self.task_a.id]),
            {"stage": self.stage_b.id, "position": -1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("position", response.data)

    def test_move_other_users_task_returns_404(self):
        response = self.client.post(
            reverse("task-move", args=[self.task_d.id]),
            {"stage": self.stage_c.id, "position": 0},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tasks_403_when_not_logged(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task(self):
        response = self.client.delete(reverse("task-detail", args=[self.task_a.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task_a.id).exists())

    def test_stages_list_only_shows_own_stages(self):
        response = self.client.get(reverse("stage-list"))
        id_list = [stage["id"] for stage in response.data]
        self.assertIn(self.stage_a.id, id_list)
        self.assertNotIn(self.stage_c.id, id_list)

    def test_stages_filter_by_project_in_order(self):
        response = self.client.get(reverse("stage-list"), {"project": self.project_a.id})
        id_list = [stage["id"] for stage in response.data]
        self.assertEqual(id_list, [self.stage_a.id, self.stage_b.id])

    def test_stages_are_read_only(self):
        response = self.client.post(
            reverse("stage-list"),
            {"name": "Test", "project": self.project_a.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TimeEntryHelpersMixin:
    def _manual_entry(self, owner, task, date=None, minutes=30):
        date = date or timezone.localdate()
        return TimeEntry.objects.create(
            owner=owner, task=task, date=date, minutes=minutes, source=TimeEntry.Source.MANUAL
        )

    # No intervals on purpose: the totals only read the entry's minutes, never the
    # exact times behind it.
    def _stopped_timer_entry(self, owner, task, date=None, minutes=45):
        date = date or timezone.localdate()
        started_at = timezone.now()
        ended_at = started_at + timedelta(minutes=minutes)
        return TimeEntry.objects.create(
            owner=owner,
            date=date,
            task=task,
            started_at=started_at,
            ended_at=ended_at,
            minutes=minutes,
        )

    # No minutes on purpose: a real open session has minutes=NULL until stop. With
    # minutes=0 the "open session not counted" test would pass even if Sum counted it.
    def _open_timer_entry(self, owner, task, date=None):
        date = date or timezone.localdate()
        started_at = timezone.now()
        return TimeEntry.objects.create(owner=owner, task=task, date=date, started_at=started_at)


class TaskLoggedMinutesTests(TimeEntryHelpersMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="testuser", password="test")
        cls.project_a = Project.objects.create(owner=cls.user, name="Project A")
        cls.stage_a = Stage.objects.create(project=cls.project_a, name="Stage A")
        cls.task_a = Task.objects.create(project=cls.project_a, stage=cls.stage_a, title="Task A")
        cls.task_b = Task.objects.create(project=cls.project_a, stage=cls.stage_a, title="Task B")

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_task_without_entries_has_zero(self):
        response = self.client.get(reverse("task-detail", args=[self.task_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 0)

    def test_sums_manual_and_stopped_timer_entries(self):
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._stopped_timer_entry(owner=self.user, task=self.task_a, minutes=45)
        response = self.client.get(reverse("task-detail", args=[self.task_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 75)

    def test_open_session_not_counted(self):
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._open_timer_entry(owner=self.user, task=self.task_a)
        response = self.client.get(reverse("task-detail", args=[self.task_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 30)

    def test_list_sums_each_task_separately(self):
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._manual_entry(owner=self.user, task=self.task_b, minutes=45)
        response = self.client.get(reverse("task-list"), {"project": self.project_a.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        minutes = {e["id"]: e["logged_minutes"] for e in response.data}
        self.assertEqual(minutes[self.task_a.id], 30)
        self.assertEqual(minutes[self.task_b.id], 45)

    def test_create_response_includes_logged_minutes(self):
        response = self.client.post(
            reverse("task-list"), {"project": self.project_a.id, "title": "New Task"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["logged_minutes"], 0)

    def test_update_response_keeps_logged_minutes(self):
        # A non-zero total on purpose: with no entries, a response that wrongly
        # reset the total to 0 would still pass.
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._stopped_timer_entry(owner=self.user, task=self.task_a, minutes=45)
        response = self.client.patch(
            reverse("task-detail", args=[self.task_a.id]), {"title": "New Task"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 75)


class ProjectLoggedMinutesTests(TimeEntryHelpersMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="testuser", password="test")
        cls.project_a = Project.objects.create(owner=cls.user, name="Project A")
        cls.stage_a = Stage.objects.create(project=cls.project_a, name="Stage A")
        cls.task_a = Task.objects.create(project=cls.project_a, stage=cls.stage_a, title="Task A")
        cls.task_b = Task.objects.create(project=cls.project_a, stage=cls.stage_a, title="Task B")
        cls.project_b = Project.objects.create(owner=cls.user, name="Project B")
        cls.stage_b = Stage.objects.create(project=cls.project_b, name="Stage B")
        cls.task_c = Task.objects.create(project=cls.project_b, stage=cls.stage_b, title="Task C")

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_project_without_entries_has_zero(self):
        response = self.client.get(reverse("project-detail", args=[self.project_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 0)

    def test_sums_entries_across_tasks(self):
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._stopped_timer_entry(owner=self.user, task=self.task_b, minutes=45)
        response = self.client.get(reverse("project-detail", args=[self.project_a.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 75)

    def test_list_sums_each_project_separately(self):
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._manual_entry(owner=self.user, task=self.task_c, minutes=45)
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        minutes = {e["id"]: e["logged_minutes"] for e in response.data}
        self.assertEqual(minutes[self.project_a.id], 30)
        self.assertEqual(minutes[self.project_b.id], 45)

    def test_archived_list_includes_total(self):
        self.project_b.archived_at = timezone.now()
        self.project_b.save()
        self._manual_entry(owner=self.user, task=self.task_c, minutes=45)
        response = self.client.get(reverse("project-list"), {"archived": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        minutes = {e["id"]: e["logged_minutes"] for e in response.data}
        self.assertNotIn(self.project_a.id, minutes)
        self.assertEqual(minutes[self.project_b.id], 45)

    def test_create_response_includes_logged_minutes(self):
        response = self.client.post(reverse("project-list"), {"name": "New Project"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["logged_minutes"], 0)

    def test_update_response_keeps_logged_minutes(self):
        self._manual_entry(owner=self.user, task=self.task_a, minutes=30)
        self._manual_entry(owner=self.user, task=self.task_b, minutes=45)
        response = self.client.patch(
            reverse("project-detail", args=[self.project_a.id]), {"name": "New name"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["logged_minutes"], 75)
