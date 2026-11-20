from django.contrib import admin

from .models import TimeEntry, TimerInterval


class TimerIntervalInline(admin.TabularInline):
    model = TimerInterval
    # No empty rows: a blank interval filled in by mistake (no ended_at) would
    # start a running timer. Intervals are added on purpose.
    extra = 0


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["task", "date", "source", "mode", "started_at", "ended_at", "minutes"]
    list_filter = ["source", "mode", "date"]
    search_fields = ["task__title", "description"]
    date_hierarchy = "date"
    readonly_fields = ["created_at", "updated_at"]
    inlines = [TimerIntervalInline]
