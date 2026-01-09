"""Reports app configuration."""
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Configuration for reports app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
    verbose_name = '测试报告'
