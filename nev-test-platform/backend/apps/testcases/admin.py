"""Admin configuration for testcases app."""
from django.contrib import admin
from .models import TestCase, TestCaseResult


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    """Admin configuration for TestCase model."""
    
    list_display = ['case_code', 'name', 'task', 'priority', 'status', 'module']
    list_filter = ['priority', 'status', 'task', 'module']
    search_fields = ['name', 'case_code', 'description', 'alm_case_id']
    ordering = ['execution_order', '-created_at']


@admin.register(TestCaseResult)
class TestCaseResultAdmin(admin.ModelAdmin):
    """Admin configuration for TestCaseResult model."""
    
    list_display = ['test_case', 'execution', 'status', 'duration_ms', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['test_case__name', 'test_case__case_code']
    ordering = ['-created_at']
