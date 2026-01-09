"""Test device models for ECU/VCU and other automotive devices."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TestDevice(models.Model):
    """Test device model for automotive testing devices."""
    
    class DeviceType(models.TextChoices):
        """Device type choices."""
        ECU = 'ecu', _('电子控制单元(ECU)')
        VCU = 'vcu', _('整车控制器(VCU)')
        BMS = 'bms', _('电池管理系统(BMS)')
        MCU = 'mcu', _('电机控制器(MCU)')
        TBOX = 'tbox', _('车载终端(T-BOX)')
        IVI = 'ivi', _('车载信息娱乐(IVI)')
        ADAS = 'adas', _('高级驾驶辅助(ADAS)')
        OBC = 'obc', _('车载充电机(OBC)')
        DCDC = 'dcdc', _('DC-DC转换器')
        OTHER = 'other', _('其他')
    
    class Status(models.TextChoices):
        """Device status choices."""
        AVAILABLE = 'available', _('可用')
        IN_USE = 'in_use', _('使用中')
        UPGRADING = 'upgrading', _('升级中')
        OFFLINE = 'offline', _('离线')
        FAULTY = 'faulty', _('故障')
    
    name = models.CharField(_('名称'), max_length=100)
    device_type = models.CharField(
        _('设备类型'),
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.ECU
    )
    serial_number = models.CharField(_('序列号'), max_length=100, unique=True)
    
    # Version info
    hardware_version = models.CharField(_('硬件版本'), max_length=50, blank=True)
    software_version = models.CharField(_('软件版本'), max_length=50, blank=True)
    firmware_version = models.CharField(_('固件版本'), max_length=50, blank=True)
    
    # Connection info
    connection_type = models.CharField(_('连接类型'), max_length=50, blank=True)  # CAN, Ethernet, USB
    connection_params = models.JSONField(_('连接参数'), default=dict, blank=True)
    
    # Status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE
    )
    
    # Environment relationship
    environment = models.ForeignKey(
        'environments.TestEnvironment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='devices',
        verbose_name=_('所属环境')
    )
    
    # Device info
    manufacturer = models.CharField(_('制造商'), max_length=100, blank=True)
    model = models.CharField(_('型号'), max_length=100, blank=True)
    description = models.TextField(_('描述'), blank=True)
    tags = models.JSONField(_('标签'), default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_devices'
        verbose_name = _('测试设备')
        verbose_name_plural = _('测试设备')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_device_type_display()}) - {self.serial_number}"


class DeviceUpgradeHistory(models.Model):
    """Device upgrade history model."""
    
    class Status(models.TextChoices):
        """Upgrade status choices."""
        PENDING = 'pending', _('等待中')
        IN_PROGRESS = 'in_progress', _('进行中')
        SUCCESS = 'success', _('成功')
        FAILED = 'failed', _('失败')
        ROLLED_BACK = 'rolled_back', _('已回滚')
    
    device = models.ForeignKey(
        TestDevice,
        on_delete=models.CASCADE,
        related_name='upgrade_history',
        verbose_name=_('设备')
    )
    artifact = models.ForeignKey(
        'artifacts.Artifact',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('制品')
    )
    
    # Version info
    from_version = models.CharField(_('原版本'), max_length=50, blank=True)
    to_version = models.CharField(_('目标版本'), max_length=50)
    
    # Status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Timing
    started_at = models.DateTimeField(_('开始时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)
    
    # Result
    error_message = models.TextField(_('错误信息'), blank=True)
    log = models.TextField(_('日志'), blank=True)
    
    # Operator
    operated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('操作人')
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        db_table = 'device_upgrade_history'
        verbose_name = _('设备升级记录')
        verbose_name_plural = _('设备升级记录')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.device.name}: {self.from_version} -> {self.to_version}"
