"""Test report models."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TestReport(models.Model):
    """Test report model for execution reports."""
    
    # Execution relationship
    execution = models.OneToOneField(
        'tasks.TaskExecution',
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name=_('执行记录')
    )
    
    # Report info
    title = models.CharField(_('标题'), max_length=200)
    summary = models.TextField(_('摘要'), blank=True)
    
    # Statistics
    total_cases = models.IntegerField(_('总用例数'), default=0)
    passed_cases = models.IntegerField(_('通过数'), default=0)
    failed_cases = models.IntegerField(_('失败数'), default=0)
    skipped_cases = models.IntegerField(_('跳过数'), default=0)
    blocked_cases = models.IntegerField(_('阻塞数'), default=0)
    error_cases = models.IntegerField(_('错误数'), default=0)
    
    # Pass rate
    pass_rate = models.FloatField(_('通过率'), default=0.0)
    
    # Duration
    total_duration_seconds = models.IntegerField(_('总执行时长(秒)'), null=True, blank=True)
    
    # File paths
    html_report_path = models.CharField(_('HTML报告路径'), max_length=500, blank=True)
    pdf_report_path = models.CharField(_('PDF报告路径'), max_length=500, blank=True)
    excel_report_path = models.CharField(_('Excel报告路径'), max_length=500, blank=True)
    json_report_path = models.CharField(_('JSON报告路径'), max_length=500, blank=True)
    
    # Environment info at report time
    environment_name = models.CharField(_('环境名称'), max_length=100, blank=True)
    host_info = models.JSONField(_('主机信息'), default=dict, blank=True)
    device_info = models.JSONField(_('设备信息'), default=list, blank=True)
    
    # Version info
    software_version = models.CharField(_('软件版本'), max_length=50, blank=True)
    git_branch = models.CharField(_('Git分支'), max_length=100, blank=True)
    git_commit = models.CharField(_('Git提交'), max_length=40, blank=True)
    
    # ALM sync
    alm_synced = models.BooleanField(_('已同步ALM'), default=False)
    alm_sync_time = models.DateTimeField(_('ALM同步时间'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_reports'
        verbose_name = _('测试报告')
        verbose_name_plural = _('测试报告')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.pass_rate}%)"
