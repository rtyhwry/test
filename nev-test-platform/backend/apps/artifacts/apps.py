"""Artifacts app configuration."""
from django.apps import AppConfig


class ArtifactsConfig(AppConfig):
    """Configuration for artifacts app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.artifacts'
    verbose_name = '制品管理'
