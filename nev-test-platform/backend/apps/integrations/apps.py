"""Integrations app configuration."""
from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """Configuration for integrations app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations'
    verbose_name = '集成管理'
