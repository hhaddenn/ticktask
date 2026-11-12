from django.contrib import admin

from .models import Project, Stage, Task


class StageInline(admin.TabularInline):
    model = Stage
    extra = 3


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["owner", "name", "description", "archived_at", "created_at", "updated_at"]
    list_filter = ["archived_at"]
    search_fields = ["name"]
    inlines = [StageInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "project",
        "stage",
        "title",
        "description",
        "sequence",
        "start_date",
        "due_date",
        "deadline_notified_at",
        "estimated_minutes",
        "created_at",
        "updated_at",
    ]
    list_filter = ["project", "stage__name"]
    search_fields = ["title"]
