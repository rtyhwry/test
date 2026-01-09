"""Test task and execution models."""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class TestTask(models.Model):
    """Test task model for scheduling and managing test executions."""
    
    class ScheduleType(models.TextChoices):
        """Schedule type choices."""
        IMMEDIATE = 'immediate', _('立即执行')
        SCHEDULED = 'scheduled', _('定时执行')
        CRON = 'cron', _('周期执行')
        MANUAL = 'manual', _('手动触发')
    
    class Status(models.TextChoices):
        """Task status choices."""
        DRAFT = 'draft', _('草稿')
        PENDING = 'pending', _('待执行')
        QUEUED = 'queued', _('排队中')
        RUNNING = 'running', _('执行中')
        COMPLETED = 'completed', _('已完成')
        FAILED = 'failed', _('失败')
        CANCELLED = 'cancelled', _('已取消')
        PAUSED = 'paused', _('已暂停')
    
    name = models.CharField(_('任务名称'), max_length=200)
    description = models.TextField(_('描述'), blank=True)
    
    # Project relationship
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('所属项目')
    )
    
    # Environment relationship
    environment = models.ForeignKey(
        'environments.TestEnvironment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('测试环境')
    )
    
    # Scheduling
    schedule_type = models.CharField(
        _('调度类型'),
        max_length=20,
        choices=ScheduleType.choices,
        default=ScheduleType.MANUAL
    )
    scheduled_time = models.DateTimeField(_('计划执行时间'), null=True, blank=True)
    cron_expression = models.CharField(_('Cron表达式'), max_length=100, blank=True)
    timezone = models.CharField(_('时区'), max_length=50, default='Asia/Shanghai')
    
    # Upgrade configuration
    need_upgrade = models.BooleanField(_('需要升级'), default=False)
    artifact = models.ForeignKey(
        'artifacts.Artifact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('升级制品')
    )
    
    # Git configuration
    git_repo_url = models.URLField(_('Git仓库地址'), max_length=500, blank=True)
    git_branch = models.CharField(_('Git分支'), max_length=100, default='main')
    git_tag = models.CharField(_('Git标签'), max_length=100, blank=True)
    test_script_path = models.CharField(_('测试脚本路径'), max_length=500, blank=True)
    test_command = models.TextField(_('测试命令'), blank=True)
    
    # ALM integration
    alm_task_id = models.CharField(_('ALM任务ID'), max_length=100, blank=True)
    alm_test_set_id = models.CharField(_('ALM测试集ID'), max_length=100, blank=True)
    
    # Execution configuration
    timeout_minutes = models.IntegerField(_('超时时间(分钟)'), default=60)
    retry_count = models.IntegerField(_('重试次数'), default=0)
    retry_interval_seconds = models.IntegerField(_('重试间隔(秒)'), default=60)
    
    # Priority (higher = more important)
    priority = models.IntegerField(_('优先级'), default=5)
    
    # Status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    is_enabled = models.BooleanField(_('是否启用'), default=True)
    
    # Creator
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name=_('创建人')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_tasks'
        verbose_name = _('测试任务')
        verbose_name_plural = _('测试任务')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def last_execution(self):
        """Get last execution of this task."""
        return self.executions.order_by('-created_at').first()


class TaskExecution(models.Model):
    """Task execution record model."""
    
    class Status(models.TextChoices):
        """Execution status choices."""
        PENDING = 'pending', _('等待中')
        PREPARING = 'preparing', _('准备中')
        UPGRADING = 'upgrading', _('升级中')
        PULLING_CODE = 'pulling_code', _('拉取代码')
        RUNNING = 'running', _('执行中')
        COMPLETED = 'completed', _('已完成')
        FAILED = 'failed', _('失败')
        CANCELLED = 'cancelled', _('已取消')
        TIMEOUT = 'timeout', _('超时')
    
    class TriggerType(models.TextChoices):
        """Trigger type choices."""
        MANUAL = 'manual', _('手动触发')
        SCHEDULED = 'scheduled', _('定时触发')
        API = 'api', _('API触发')
        WEBHOOK = 'webhook', _('Webhook触发')
    
    # Task relationship
    task = models.ForeignKey(
        TestTask,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('测试任务')
    )
    
    # Environment relationship
    environment = models.ForeignKey(
        'environments.TestEnvironment',
        on_delete=models.SET_NULL,
        null=True,
        related_name='executions',
        verbose_name=_('测试环境')
    )
    
    # Execution info
    execution_number = models.IntegerField(_('执行序号'))
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Timing
    start_time = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    duration_seconds = models.IntegerField(_('执行时长(秒)'), null=True, blank=True)
    
    # Trigger info
    triggered_by = models.CharField(
        _('触发方式'),
        max_length=20,
        choices=TriggerType.choices,
        default=TriggerType.MANUAL
    )
    triggered_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_executions',
        verbose_name=_('触发人')
    )
    
    # Version info at execution time
    artifact_version = models.CharField(_('制品版本'), max_length=50, blank=True)
    git_commit = models.CharField(_('Git提交'), max_length=40, blank=True)
    
    # Results
    total_cases = models.IntegerField(_('总用例数'), default=0)
    passed_cases = models.IntegerField(_('通过数'), default=0)
    failed_cases = models.IntegerField(_('失败数'), default=0)
    skipped_cases = models.IntegerField(_('跳过数'), default=0)
    
    # Logs and artifacts
    log_path = models.CharField(_('日志路径'), max_length=500, blank=True)
    error_message = models.TextField(_('错误信息'), blank=True)
    
    # Celery task info
    celery_task_id = models.CharField(_('Celery任务ID'), max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'task_executions'
        verbose_name = _('任务执行')
        verbose_name_plural = _('任务执行')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.name} #{self.execution_number}"
    
    @property
    def pass_rate(self):
        """Calculate pass rate."""
        if self.total_cases == 0:
            return 0
        return round(self.passed_cases / self.total_cases * 100, 2)
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate execution number."""
        if not self.execution_number:
            last_execution = TaskExecution.objects.filter(task=self.task).order_by('-execution_number').first()
            self.execution_number = (last_execution.execution_number + 1) if last_execution else 1
        super().save(*args, **kwargs)


class ExecutionLog(models.Model):
    """Execution log model for storing real-time logs."""
    
    class Level(models.TextChoices):
        """Log level choices."""
        DEBUG = 'debug', 'DEBUG'
        INFO = 'info', 'INFO'
        WARNING = 'warning', 'WARNING'
        ERROR = 'error', 'ERROR'
    
    execution = models.ForeignKey(
        TaskExecution,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('执行记录')
    )
    
    timestamp = models.DateTimeField(_('时间戳'), auto_now_add=True)
    level = models.CharField(
        _('级别'),
        max_length=10,
        choices=Level.choices,
        default=Level.INFO
    )
    stage = models.CharField(_('阶段'), max_length=50)
    message = models.TextField(_('消息'))
    
    class Meta:
        db_table = 'execution_logs'
        verbose_name = _('执行日志')
        verbose_name_plural = _('执行日志')
        ordering = ['timestamp']
    
    def __str__(self):
        return f"[{self.level}] {self.stage}: {self.message[:50]}"
