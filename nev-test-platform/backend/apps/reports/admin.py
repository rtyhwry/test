"""Admin configuration for reports app."""
from django.contrib import admin
from .models import TestReport


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    """Admin configuration for TestReport model."""
    
    list_display = ['title', 'execution', 'pass_rate', 'total_cases', 'alm_synced', 'created_at']
    list_filter = ['alm_synced', 'created_at']
    search_fields = ['title', 'execution__task__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
