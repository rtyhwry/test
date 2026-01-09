"""Test environment serializers for API."""
from rest_framework import serializers
from .models import TestEnvironment
from apps.hosts.serializers import TestHostSerializer
from apps.devices.serializers import TestDeviceSerializer


class TestEnvironmentSerializer(serializers.ModelSerializer):
    """Serializer for test environment details."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    host_info = TestHostSerializer(source='host', read_only=True)
    devices = TestDeviceSerializer(many=True, read_only=True)
    locked_by_name = serializers.CharField(source='locked_by.username', read_only=True)
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestEnvironment
        fields = [
            'id', 'name', 'code', 'project', 'project_name',
            'host', 'host_info', 'status', 'status_display',
            'locked_by', 'locked_by_name', 'locked_at', 'lock_reason', 'lock_expires_at',
            'is_auto_release', 'max_lock_hours',
            'description', 'tags', 'devices', 'device_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'locked_by', 'locked_at', 'lock_expires_at', 'created_at', 'updated_at']
    
    def get_device_count(self, obj):
        """Get count of devices in environment."""
        return obj.devices.count()


class TestEnvironmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a test environment."""
    
    class Meta:
        model = TestEnvironment
        fields = [
            'name', 'code', 'project', 'host',
            'description', 'tags', 'is_auto_release', 'max_lock_hours'
        ]
    
    def validate_code(self, value):
        """Validate environment code format."""
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError('环境代码只能包含字母、数字、下划线和横线')
        return value.upper()


class TestEnvironmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a test environment."""
    
    class Meta:
        model = TestEnvironment
        fields = [
            'name', 'host', 'description', 'tags',
            'is_auto_release', 'max_lock_hours'
        ]


class EnvironmentLockSerializer(serializers.Serializer):
    """Serializer for environment lock request."""
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    duration_hours = serializers.IntegerField(min_value=1, max_value=168, default=24)  # Max 1 week


class EnvironmentUnlockSerializer(serializers.Serializer):
    """Serializer for environment unlock request."""
    force = serializers.BooleanField(default=False)
