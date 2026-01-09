"""Test task serializers for API."""
from rest_framework import serializers
from .models import TestTask, TaskExecution, ExecutionLog
from apps.users.serializers import UserSerializer


class TestTaskSerializer(serializers.ModelSerializer):
    """Serializer for test task details."""
    schedule_type_display = serializers.CharField(source='get_schedule_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    artifact_info = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    last_execution_info = serializers.SerializerMethodField()
    execution_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestTask
        fields = [
            'id', 'name', 'description',
            'project', 'project_name', 'environment', 'environment_name',
            'schedule_type', 'schedule_type_display', 'scheduled_time', 'cron_expression', 'timezone',
            'need_upgrade', 'artifact', 'artifact_info',
            'git_repo_url', 'git_branch', 'git_tag', 'test_script_path', 'test_command',
            'alm_task_id', 'alm_test_set_id',
            'timeout_minutes', 'retry_count', 'retry_interval_seconds', 'priority',
            'status', 'status_display', 'is_enabled',
            'created_by', 'created_by_name', 'last_execution_info', 'execution_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_by', 'created_at', 'updated_at']
    
    def get_artifact_info(self, obj):
        """Get artifact info."""
        if obj.artifact:
            return {
                'id': obj.artifact.id,
                'name': obj.artifact.name,
                'version': obj.artifact.version
            }
        return None
    
    def get_last_execution_info(self, obj):
        """Get last execution info."""
        last_exec = obj.last_execution
        if last_exec:
            return {
                'id': last_exec.id,
                'status': last_exec.status,
                'start_time': last_exec.start_time,
                'pass_rate': last_exec.pass_rate
            }
        return None
    
    def get_execution_count(self, obj):
        """Get total execution count."""
        return obj.executions.count()


class TestTaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a test task."""
    
    class Meta:
        model = TestTask
        fields = [
            'name', 'description', 'project', 'environment',
            'schedule_type', 'scheduled_time', 'cron_expression', 'timezone',
            'need_upgrade', 'artifact',
            'git_repo_url', 'git_branch', 'git_tag', 'test_script_path', 'test_command',
            'alm_task_id', 'alm_test_set_id',
            'timeout_minutes', 'retry_count', 'retry_interval_seconds', 'priority'
        ]
    
    def validate(self, attrs):
        """Validate task configuration."""
        schedule_type = attrs.get('schedule_type')
        
        if schedule_type == TestTask.ScheduleType.SCHEDULED:
            if not attrs.get('scheduled_time'):
                raise serializers.ValidationError({
                    'scheduled_time': '定时执行任务必须指定执行时间'
                })
        
        if schedule_type == TestTask.ScheduleType.CRON:
            if not attrs.get('cron_expression'):
                raise serializers.ValidationError({
                    'cron_expression': '周期执行任务必须指定Cron表达式'
                })
        
        if attrs.get('need_upgrade') and not attrs.get('artifact'):
            raise serializers.ValidationError({
                'artifact': '需要升级时必须指定制品'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create task with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TestTaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a test task."""
    
    class Meta:
        model = TestTask
        fields = [
            'name', 'description', 'environment',
            'schedule_type', 'scheduled_time', 'cron_expression', 'timezone',
            'need_upgrade', 'artifact',
            'git_repo_url', 'git_branch', 'git_tag', 'test_script_path', 'test_command',
            'timeout_minutes', 'retry_count', 'retry_interval_seconds', 'priority',
            'is_enabled'
        ]


class ExecuteTaskSerializer(serializers.Serializer):
    """Serializer for task execution request."""
    environment_id = serializers.IntegerField(required=False)
    force_upgrade = serializers.BooleanField(default=False)


class TaskExecutionSerializer(serializers.ModelSerializer):
    """Serializer for task execution details."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    triggered_by_display = serializers.CharField(source='get_triggered_by_display', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    triggered_user_name = serializers.CharField(source='triggered_user.username', read_only=True)
    pass_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TaskExecution
        fields = [
            'id', 'task', 'task_name', 'environment', 'environment_name',
            'execution_number', 'status', 'status_display',
            'start_time', 'end_time', 'duration_seconds',
            'triggered_by', 'triggered_by_display', 'triggered_user', 'triggered_user_name',
            'artifact_version', 'git_commit',
            'total_cases', 'passed_cases', 'failed_cases', 'skipped_cases', 'pass_rate',
            'log_path', 'error_message', 'celery_task_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'execution_number', 'created_at', 'updated_at']


class ExecutionLogSerializer(serializers.ModelSerializer):
    """Serializer for execution log."""
    
    class Meta:
        model = ExecutionLog
        fields = ['id', 'timestamp', 'level', 'stage', 'message']
        read_only_fields = ['id', 'timestamp']
