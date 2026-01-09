"""Test host models for remote test execution machines."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TestHost(models.Model):
    """Test host model for machines that execute tests."""
    
    class Status(models.TextChoices):
        """Host status choices."""
        ONLINE = 'online', _('在线')
        OFFLINE = 'offline', _('离线')
        BUSY = 'busy', _('忙碌')
        MAINTENANCE = 'maintenance', _('维护中')
    
    class OSType(models.TextChoices):
        """Host OS type choices."""
        LINUX = 'linux', _('Linux')
        WINDOWS = 'windows', _('Windows')
        MACOS = 'macos', _('macOS')
    
    name = models.CharField(_('名称'), max_length=100, unique=True)
    hostname = models.CharField(_('主机名'), max_length=255)
    ip_address = models.GenericIPAddressField(_('IP地址'))
    ssh_port = models.IntegerField(_('SSH端口'), default=22)
    ssh_username = models.CharField(_('SSH用户名'), max_length=50, default='root')
    ssh_password = models.CharField(_('SSH密码'), max_length=255, blank=True)
    ssh_key = models.TextField(_('SSH私钥'), blank=True)
    
    # System info
    os_type = models.CharField(
        _('操作系统'),
        max_length=20,
        choices=OSType.choices,
        default=OSType.LINUX
    )
    os_version = models.CharField(_('系统版本'), max_length=50, blank=True)
    cpu_cores = models.IntegerField(_('CPU核心数'), null=True, blank=True)
    memory_gb = models.FloatField(_('内存(GB)'), null=True, blank=True)
    disk_gb = models.FloatField(_('磁盘(GB)'), null=True, blank=True)
    
    # Status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE
    )
    last_heartbeat = models.DateTimeField(_('最后心跳'), null=True, blank=True)
    
    # Workspace
    workspace_path = models.CharField(_('工作目录'), max_length=500, default='/home/test/workspace')
    
    # Metadata
    tags = models.JSONField(_('标签'), default=list, blank=True)
    description = models.TextField(_('描述'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_hosts'
        verbose_name = _('测试主机')
        verbose_name_plural = _('测试主机')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
