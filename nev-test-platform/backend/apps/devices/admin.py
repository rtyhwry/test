"""Admin configuration for devices app."""
from django.contrib import admin
from .models import TestDevice, DeviceUpgradeHistory


@admin.register(TestDevice)
class TestDeviceAdmin(admin.ModelAdmin):
    """Admin configuration for TestDevice model."""
    
    list_display = ['name', 'device_type', 'serial_number', 'software_version', 'status', 'environment']
    list_filter = ['device_type', 'status', 'environment', 'created_at']
    search_fields = ['name', 'serial_number', 'manufacturer', 'model', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('name', 'device_type', 'serial_number', 'description')}),
        ('版本信息', {'fields': ('hardware_version', 'software_version', 'firmware_version')}),
        ('连接配置', {'fields': ('connection_type', 'connection_params')}),
        ('设备信息', {'fields': ('manufacturer', 'model', 'tags')}),
        ('状态', {'fields': ('status', 'environment')}),
    )


@admin.register(DeviceUpgradeHistory)
class DeviceUpgradeHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for DeviceUpgradeHistory model."""
    
    list_display = ['device', 'from_version', 'to_version', 'status', 'operated_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['device__name', 'from_version', 'to_version']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
