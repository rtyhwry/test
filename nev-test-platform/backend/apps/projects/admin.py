"""Admin configuration for projects app."""
from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    
    list_display = ['name', 'code', 'owner', 'created_at']
    list_filter = ['owner', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('name', 'code', 'description', 'owner')}),
        ('Git配置', {'fields': ('git_repo_url', 'git_default_branch')}),
        ('ALM配置', {'fields': ('alm_project_id',)}),
    )
