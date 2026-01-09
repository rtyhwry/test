"""Admin configuration for hosts app."""
from django.contrib import admin
from .models import TestHost


@admin.register(TestHost)
class TestHostAdmin(admin.ModelAdmin):
    """Admin configuration for TestHost model."""
    
    list_display = ['name', 'ip_address', 'os_type', 'status', 'last_heartbeat']
    list_filter = ['status', 'os_type', 'created_at']
    search_fields = ['name', 'hostname', 'ip_address', 'description']
    ordering = ['-created_at']
    readonly_fields = ['status', 'last_heartbeat', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('name', 'hostname', 'ip_address', 'description')}),
        ('SSH配置', {'fields': ('ssh_port', 'ssh_username', 'ssh_password', 'ssh_key')}),
        ('系统信息', {'fields': ('os_type', 'os_version', 'cpu_cores', 'memory_gb', 'disk_gb')}),
        ('状态', {'fields': ('status', 'last_heartbeat', 'workspace_path')}),
        ('元数据', {'fields': ('tags',)}),
    )
