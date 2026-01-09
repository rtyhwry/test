"""Project models for organizing test resources."""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """Project model for grouping test environments and tasks."""
    
    name = models.CharField(_('项目名称'), max_length=100, unique=True)
    code = models.CharField(_('项目代码'), max_length=20, unique=True)
    description = models.TextField(_('描述'), blank=True)
    
    # Git repository configuration
    git_repo_url = models.URLField(_('Git仓库地址'), max_length=500, blank=True)
    git_default_branch = models.CharField(_('默认分支'), max_length=100, default='main')
    
    # ALM configuration
    alm_project_id = models.CharField(_('ALM项目ID'), max_length=100, blank=True)
    
    # Owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_projects',
        verbose_name=_('负责人')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = _('项目')
        verbose_name_plural = _('项目')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
