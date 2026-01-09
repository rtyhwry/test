"""Artifact serializers for API."""
from rest_framework import serializers
from .models import Artifact


class ArtifactSerializer(serializers.ModelSerializer):
    """Serializer for artifact details."""
    artifact_type_display = serializers.CharField(source='get_artifact_type_display', read_only=True)
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Artifact
        fields = [
            'id', 'name', 'version', 'artifact_type', 'artifact_type_display',
            'repository', 'group_id', 'artifact_id',
            'file_name', 'file_size', 'file_size_display', 'checksum', 'download_url',
            'target_device_type', 'description', 'release_notes',
            'build_number', 'branch', 'commit_hash',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_size_display(self, obj):
        """Get human-readable file size."""
        if not obj.file_size:
            return None
        
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class ArtifactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an artifact."""
    
    class Meta:
        model = Artifact
        fields = [
            'name', 'version', 'artifact_type',
            'repository', 'group_id', 'artifact_id',
            'file_name', 'file_size', 'checksum', 'download_url',
            'target_device_type', 'description', 'release_notes',
            'build_number', 'branch', 'commit_hash'
        ]


class ArtifactSyncSerializer(serializers.Serializer):
    """Serializer for artifact sync request."""
    repository = serializers.CharField(max_length=200)
    group_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    artifact_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    version_pattern = serializers.CharField(max_length=100, required=False, allow_blank=True)
