from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "archived_at", "created_at", "updated_at"]
        read_only_fields = ["archived_at", "created_at", "updated_at"]
