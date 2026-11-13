from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
        response = self.client.patch(reverse("project-detail", args=[self.project_a.id]), {"name": "Renamed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project_a.refresh_from_db()
        self.assertEqual(self.project_a.name, "Renamed")

    def test_archive_hides_project_from_list(self):
        self.client.post(reverse("project-archive", args=[self.project_a.id]))
        self.project_a.refresh_from_db()
        self.assertIsNotNone(self.project_a.archived_at)
        response = self.client.get(reverse("project-list"))
        ids = [project["id"] for project in response.data]
        self.assertNotIn(self.project_a.id, ids)
        response = self.client.get(reverse("project-list"), {"archived": "true"})
        ids = [project["id"] for project in response.data]
        self.assertIn(self.project_a.id, ids)

    def test_unarchive_restores_project(self):
        pass
        #TODO
        # Põe o projeto arquivado diretamente: self.project_a.archived_at = timezone.now() e self.project_a.save(). O timezone vem de django.utils.
        # POST a reverse("project-unarchive", args=[...]).
        # Verifica que o status é 200, e não 404.
        # Faz refresh_from_db() e verifica com o assertIsNone que o archived_at voltou a None.
    
    def test_delete_not_allowed(self):
        pass
        #TODO
        # self.client.delete(...) ao detalhe do projeto.
        # Verifica que o status é HTTP_405_METHOD_NOT_ALLOWED.
        # Verifica que o projeto continua a existir: Project.objects.filter(id=...).exists() dá True.