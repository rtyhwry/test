"""Admin configuration for artifacts app."""
from django.contrib import admin
from .models import Artifact


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    """Admin configuration for Artifact model."""
    
    list_display = ['name', 'version', 'artifact_type', 'repository', 'target_device_type', 'created_at']
    list_filter = ['artifact_type', 'repository', 'target_device_type', 'created_at']
    search_fields = ['name', 'version', 'description', 'artifact_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {'fields': ('name', 'version', 'artifact_type', 'description')}),
        ('仓库信息', {'fields': ('repository', 'group_id', 'artifact_id')}),
        ('文件信息', {'fields': ('file_name', 'file_size', 'checksum', 'download_url', 'local_path')}),
        ('构建信息', {'fields': ('build_number', 'branch', 'commit_hash')}),
        ('目标', {'fields': ('target_device_type',)}),
        ('发布说明', {'fields': ('release_notes',)}),
    )
