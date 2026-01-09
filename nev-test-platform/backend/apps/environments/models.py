"""Test environment models combining host and devices."""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TestEnvironment(models.Model):
    """Test environment model combining host and devices."""
    
    class Status(models.TextChoices):
        """Environment status choices."""
        AVAILABLE = 'available', _('可用')
        LOCKED = 'locked', _('已锁定')
        IN_USE = 'in_use', _('使用中')
        MAINTENANCE = 'maintenance', _('维护中')
        OFFLINE = 'offline', _('离线')
    
    name = models.CharField(_('名称'), max_length=100)
    code = models.CharField(_('环境代码'), max_length=50, unique=True)
    
    # Project relationship
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='environments',
        verbose_name=_('所属项目')
    )
    
    # Host relationship
    host = models.ForeignKey(
        'hosts.TestHost',
        on_delete=models.PROTECT,
        related_name='environments',
        verbose_name=_('测试主机')
    )
    
    # Status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    
    # Lock info
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_environments',
        verbose_name=_('锁定人')
    )
    locked_at = models.DateTimeField(_('锁定时间'), null=True, blank=True)
    lock_reason = models.CharField(_('锁定原因'), max_length=500, blank=True)
    lock_expires_at = models.DateTimeField(_('锁定过期时间'), null=True, blank=True)
    
    # Configuration
    is_auto_release = models.BooleanField(_('自动释放'), default=True)
    max_lock_hours = models.IntegerField(_('最大锁定时长(小时)'), default=24)
    
    # Metadata
    description = models.TextField(_('描述'), blank=True)
    tags = models.JSONField(_('标签'), default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_environments'
        verbose_name = _('测试环境')
        verbose_name_plural = _('测试环境')
        ordering = ['-created_at']
        unique_together = [['project', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def is_available(self):
        """Check if environment is available for use."""
        return self.status == self.Status.AVAILABLE
    
    @property
    def is_locked(self):
        """Check if environment is locked."""
        return self.status == self.Status.LOCKED or self.locked_by is not None
