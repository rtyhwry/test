"""Artifact models for software versions from artifact repository."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Artifact(models.Model):
    """Artifact model for managing software versions."""
    
    class ArtifactType(models.TextChoices):
        """Artifact type choices."""
        FIRMWARE = 'firmware', _('固件')
        SOFTWARE = 'software', _('软件')
        BOOTLOADER = 'bootloader', _('引导程序')
        CALIBRATION = 'calibration', _('标定数据')
        CONFIG = 'config', _('配置文件')
        OTHER = 'other', _('其他')
    
    name = models.CharField(_('名称'), max_length=200)
    version = models.CharField(_('版本'), max_length=50)
    artifact_type = models.CharField(
        _('类型'),
        max_length=20,
        choices=ArtifactType.choices,
        default=ArtifactType.SOFTWARE
    )
    
    # Repository info
    repository = models.CharField(_('仓库'), max_length=200)
    group_id = models.CharField(_('组ID'), max_length=200, blank=True)
    artifact_id = models.CharField(_('制品ID'), max_length=200)
    
    # File info
    file_name = models.CharField(_('文件名'), max_length=255)
    file_size = models.BigIntegerField(_('文件大小(字节)'), null=True, blank=True)
    checksum = models.CharField(_('校验和(SHA256)'), max_length=64, blank=True)
    download_url = models.URLField(_('下载地址'), max_length=1000)
    local_path = models.CharField(_('本地路径'), max_length=500, blank=True)
    
    # Target
    target_device_type = models.CharField(_('目标设备类型'), max_length=50, blank=True)
    
    # Metadata
    description = models.TextField(_('描述'), blank=True)
    release_notes = models.TextField(_('发布说明'), blank=True)
    build_number = models.CharField(_('构建号'), max_length=50, blank=True)
    branch = models.CharField(_('分支'), max_length=100, blank=True)
    commit_hash = models.CharField(_('提交哈希'), max_length=40, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'artifacts'
        verbose_name = _('制品')
        verbose_name_plural = _('制品')
        ordering = ['-created_at']
        unique_together = [['name', 'version']]
    
    def __str__(self):
        return f"{self.name} v{self.version}"
