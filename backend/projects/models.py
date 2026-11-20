from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Project(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Stage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=100)
    sequence = models.PositiveIntegerField(default=0)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["sequence", "id"]


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    stage = models.ForeignKey(Stage, on_delete=models.RESTRICT, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    sequence = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    deadline_notified_at = models.DateTimeField(null=True, blank=True)
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.project_id and self.stage_id:
            if self.stage.project_id != self.project_id:
                raise ValidationError({"stage": "Choose a stage from the task's project."})

    class Meta:
        ordering = ["stage__sequence", "sequence", "id"]
        constraints = [
            # Last line of defense: nothing (API bug, admin, script) can save a task
            # that starts after its due date. TaskSerializer.validate checks first,
            # so the API answers 400 instead of crashing with an IntegrityError (500).
            models.CheckConstraint(
                condition=Q(start_date__isnull=True)
                | Q(due_date__isnull=True)
                | Q(start_date__lte=F("due_date")),
                name="start_date_lte_due_date",
            )
        ]
