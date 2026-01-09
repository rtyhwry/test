"""Test case serializers for API."""
from rest_framework import serializers
from .models import TestCase, TestCaseResult


class TestCaseSerializer(serializers.ModelSerializer):
    """Serializer for test case details."""
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True)
    
    class Meta:
        model = TestCase
        fields = [
            'id', 'name', 'case_code', 'description',
            'task', 'task_name', 'module', 'priority', 'priority_display',
            'script_path', 'class_name', 'method_name', 'parameters',
            'expected_result', 'preconditions',
            'status', 'status_display', 'alm_case_id',
            'estimated_time', 'execution_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestCaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a test case."""
    
    class Meta:
        model = TestCase
        fields = [
            'name', 'case_code', 'description', 'task',
            'module', 'priority', 'script_path', 'class_name', 'method_name',
            'parameters', 'expected_result', 'preconditions',
            'alm_case_id', 'estimated_time', 'execution_order'
        ]


class TestCaseUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a test case."""
    
    class Meta:
        model = TestCase
        fields = [
            'name', 'description', 'module', 'priority',
            'script_path', 'class_name', 'method_name', 'parameters',
            'expected_result', 'preconditions', 'status',
            'estimated_time', 'execution_order'
        ]


class TestCaseBatchCreateSerializer(serializers.Serializer):
    """Serializer for batch creating test cases."""
    task_id = serializers.IntegerField()
    cases = TestCaseCreateSerializer(many=True)


class TestCaseResultSerializer(serializers.ModelSerializer):
    """Serializer for test case result."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    test_case_info = TestCaseSerializer(source='test_case', read_only=True)
    
    class Meta:
        model = TestCaseResult
        fields = [
            'id', 'execution', 'test_case', 'test_case_info',
            'status', 'status_display',
            'start_time', 'end_time', 'duration_ms',
            'actual_result', 'error_message', 'stack_trace',
            'screenshot_path', 'log_path', 'retry_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
