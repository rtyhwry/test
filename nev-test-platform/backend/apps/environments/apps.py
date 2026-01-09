"""Environments app configuration."""
from django.apps import AppConfig


class EnvironmentsConfig(AppConfig):
    """Configuration for environments app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.environments'
    verbose_name = '环境管理'
