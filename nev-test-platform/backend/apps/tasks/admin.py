"""Admin configuration for tasks app."""
from django.contrib import admin
from .models import TestTask, TaskExecution, ExecutionLog


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    """Admin configuration for TestTask model."""
    
    list_display = ['name', 'project', 'schedule_type', 'status', 'is_enabled', 'created_by', 'created_at']
    list_filter = ['status', 'schedule_type', 'is_enabled', 'project', 'created_at']
    search_fields = ['name', 'description', 'alm_task_id']
    ordering = ['-created_at']
    readonly_fields = ['status', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('name', 'description', 'project', 'environment')}),
        ('调度配置', {'fields': ('schedule_type', 'scheduled_time', 'cron_expression', 'timezone')}),
        ('升级配置', {'fields': ('need_upgrade', 'artifact')}),
        ('Git配置', {'fields': ('git_repo_url', 'git_branch', 'git_tag', 'test_script_path', 'test_command')}),
        ('ALM配置', {'fields': ('alm_task_id', 'alm_test_set_id')}),
        ('执行配置', {'fields': ('timeout_minutes', 'retry_count', 'retry_interval_seconds', 'priority')}),
        ('状态', {'fields': ('status', 'is_enabled', 'created_by')}),
    )


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    """Admin configuration for TaskExecution model."""
    
    list_display = ['task', 'execution_number', 'status', 'start_time', 'duration_seconds', 'pass_rate', 'triggered_by']
    list_filter = ['status', 'triggered_by', 'created_at']
    search_fields = ['task__name', 'celery_task_id']
    ordering = ['-created_at']
    readonly_fields = ['execution_number', 'pass_rate', 'created_at', 'updated_at']
    
    def pass_rate(self, obj):
        return f"{obj.pass_rate}%"
    pass_rate.short_description = '通过率'


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    """Admin configuration for ExecutionLog model."""
    
    list_display = ['execution', 'timestamp', 'level', 'stage', 'message_preview']
    list_filter = ['level', 'stage', 'timestamp']
    search_fields = ['message']
    ordering = ['-timestamp']
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = '消息'
