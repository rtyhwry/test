"""TestCases app configuration."""
from django.apps import AppConfig


class TestcasesConfig(AppConfig):
    """Configuration for testcases app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.testcases'
    verbose_name = '测试用例'
