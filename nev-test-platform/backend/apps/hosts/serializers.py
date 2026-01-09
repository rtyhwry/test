"""Test host serializers for API."""
from rest_framework import serializers
from .models import TestHost


class TestHostSerializer(serializers.ModelSerializer):
    """Serializer for test host details."""
    environment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestHost
        fields = [
            'id', 'name', 'hostname', 'ip_address', 'ssh_port', 'ssh_username',
            'os_type', 'os_version', 'cpu_cores', 'memory_gb', 'disk_gb',
            'status', 'last_heartbeat', 'workspace_path',
            'tags', 'description', 'environment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'last_heartbeat', 'created_at', 'updated_at']
    
    def get_environment_count(self, obj):
        """Get count of environments using this host."""
        return obj.environments.count()


class TestHostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a test host."""
    
    class Meta:
        model = TestHost
        fields = [
            'name', 'hostname', 'ip_address', 'ssh_port', 'ssh_username',
            'ssh_password', 'ssh_key', 'os_type', 'os_version',
            'cpu_cores', 'memory_gb', 'disk_gb', 'workspace_path',
            'tags', 'description'
        ]
        extra_kwargs = {
            'ssh_password': {'write_only': True},
            'ssh_key': {'write_only': True},
        }


class TestHostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a test host."""
    
    class Meta:
        model = TestHost
        fields = [
            'name', 'hostname', 'ip_address', 'ssh_port', 'ssh_username',
            'ssh_password', 'ssh_key', 'os_type', 'os_version',
            'cpu_cores', 'memory_gb', 'disk_gb', 'workspace_path',
            'tags', 'description'
        ]
        extra_kwargs = {
            'ssh_password': {'write_only': True},
            'ssh_key': {'write_only': True},
        }


class HostStatusSerializer(serializers.Serializer):
    """Serializer for host status response."""
    status = serializers.CharField()
    cpu_usage = serializers.FloatField()
    memory_usage = serializers.FloatField()
    disk_usage = serializers.FloatField()
    uptime = serializers.CharField()
    last_check = serializers.DateTimeField()
