"""Hosts app configuration."""
from django.apps import AppConfig


class HostsConfig(AppConfig):
    """Configuration for hosts app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hosts'
    verbose_name = '主机管理'
