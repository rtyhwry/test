"""Test report serializers for API."""
from rest_framework import serializers
from .models import TestReport


class TestReportSerializer(serializers.ModelSerializer):
    """Serializer for test report details."""
    execution_info = serializers.SerializerMethodField()
    
    class Meta:
        model = TestReport
        fields = [
            'id', 'execution', 'execution_info', 'title', 'summary',
            'total_cases', 'passed_cases', 'failed_cases', 'skipped_cases',
            'blocked_cases', 'error_cases', 'pass_rate', 'total_duration_seconds',
            'html_report_path', 'pdf_report_path', 'excel_report_path', 'json_report_path',
            'environment_name', 'host_info', 'device_info',
            'software_version', 'git_branch', 'git_commit',
            'alm_synced', 'alm_sync_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_execution_info(self, obj):
        """Get execution info."""
        return {
            'id': obj.execution.id,
            'task_name': obj.execution.task.name,
            'execution_number': obj.execution.execution_number,
            'start_time': obj.execution.start_time,
            'end_time': obj.execution.end_time
        }


class ReportGenerateSerializer(serializers.Serializer):
    """Serializer for report generation request."""
    formats = serializers.ListField(
        child=serializers.ChoiceField(choices=['html', 'pdf', 'excel', 'json']),
        default=['html']
    )
    include_logs = serializers.BooleanField(default=True)
    include_screenshots = serializers.BooleanField(default=True)


class ReportStatisticsSerializer(serializers.Serializer):
    """Serializer for report statistics."""
    total_executions = serializers.IntegerField()
    total_cases_executed = serializers.IntegerField()
    total_passed = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    average_pass_rate = serializers.FloatField()
    average_duration_seconds = serializers.FloatField()
    daily_stats = serializers.ListField(child=serializers.DictField(), required=False)
