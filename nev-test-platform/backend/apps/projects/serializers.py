"""Project serializers for API."""
from rest_framework import serializers
from .models import Project
from apps.users.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for project details."""
    owner_info = UserSerializer(source='owner', read_only=True)
    environment_count = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'description',
            'git_repo_url', 'git_default_branch', 'alm_project_id',
            'owner', 'owner_info', 'environment_count', 'task_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_environment_count(self, obj):
        """Get count of environments in project."""
        return obj.environments.count()
    
    def get_task_count(self, obj):
        """Get count of tasks in project."""
        return obj.tasks.count()


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a project."""
    
    class Meta:
        model = Project
        fields = [
            'name', 'code', 'description',
            'git_repo_url', 'git_default_branch', 'alm_project_id', 'owner'
        ]
    
    def validate_code(self, value):
        """Validate project code format."""
        if not value.isalnum():
            raise serializers.ValidationError('项目代码只能包含字母和数字')
        return value.upper()


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a project."""
    
    class Meta:
        model = Project
        fields = [
            'name', 'description',
            'git_repo_url', 'git_default_branch', 'alm_project_id', 'owner'
        ]
