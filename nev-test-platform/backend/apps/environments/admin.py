"""Admin configuration for environments app."""
from django.contrib import admin
from .models import TestEnvironment


@admin.register(TestEnvironment)
class TestEnvironmentAdmin(admin.ModelAdmin):
    """Admin configuration for TestEnvironment model."""
    
    list_display = ['name', 'code', 'project', 'host', 'status', 'locked_by', 'created_at']
    list_filter = ['status', 'project', 'host', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['-created_at']
    readonly_fields = ['locked_at', 'lock_expires_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('name', 'code', 'project', 'host', 'description')}),
        ('状态', {'fields': ('status', 'locked_by', 'locked_at', 'lock_reason', 'lock_expires_at')}),
        ('配置', {'fields': ('is_auto_release', 'max_lock_hours', 'tags')}),
    )
