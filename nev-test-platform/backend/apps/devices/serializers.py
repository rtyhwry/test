"""Test device serializers for API."""
from rest_framework import serializers
from .models import TestDevice, DeviceUpgradeHistory


class TestDeviceSerializer(serializers.ModelSerializer):
    """Serializer for test device details."""
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    
    class Meta:
        model = TestDevice
        fields = [
            'id', 'name', 'device_type', 'device_type_display', 'serial_number',
            'hardware_version', 'software_version', 'firmware_version',
            'connection_type', 'connection_params',
            'status', 'status_display', 'environment', 'environment_name',
            'manufacturer', 'model', 'description', 'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestDeviceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a test device."""
    
    class Meta:
        model = TestDevice
        fields = [
            'name', 'device_type', 'serial_number',
            'hardware_version', 'software_version', 'firmware_version',
            'connection_type', 'connection_params',
            'environment', 'manufacturer', 'model', 'description', 'tags'
        ]


class TestDeviceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a test device."""
    
    class Meta:
        model = TestDevice
        fields = [
            'name', 'device_type',
            'hardware_version', 'software_version', 'firmware_version',
            'connection_type', 'connection_params', 'status',
            'environment', 'manufacturer', 'model', 'description', 'tags'
        ]


class DeviceUpgradeRequestSerializer(serializers.Serializer):
    """Serializer for device upgrade request."""
    artifact_id = serializers.IntegerField()
    force = serializers.BooleanField(default=False)


class DeviceUpgradeHistorySerializer(serializers.ModelSerializer):
    """Serializer for device upgrade history."""
    device_name = serializers.CharField(source='device.name', read_only=True)
    artifact_name = serializers.CharField(source='artifact.name', read_only=True)
    operated_by_name = serializers.CharField(source='operated_by.username', read_only=True)
    
    class Meta:
        model = DeviceUpgradeHistory
        fields = [
            'id', 'device', 'device_name', 'artifact', 'artifact_name',
            'from_version', 'to_version', 'status',
            'started_at', 'completed_at', 'error_message',
            'operated_by', 'operated_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
