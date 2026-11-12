from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

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
