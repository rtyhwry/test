"""Test case and result models."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TestCase(models.Model):
    """Test case model for individual test cases."""
    
    class Status(models.TextChoices):
        """Test case status choices."""
        ACTIVE = 'active', _('激活')
        INACTIVE = 'inactive', _('未激活')
        DEPRECATED = 'deprecated', _('已废弃')
    
    class Priority(models.TextChoices):
        """Test case priority choices."""
        CRITICAL = 'critical', _('严重')
        HIGH = 'high', _('高')
        MEDIUM = 'medium', _('中')
        LOW = 'low', _('低')
    
    name = models.CharField(_('名称'), max_length=200)
    case_code = models.CharField(_('用例编号'), max_length=50)
    description = models.TextField(_('描述'), blank=True)
    
    # Task relationship
    task = models.ForeignKey(
        'tasks.TestTask',
        on_delete=models.CASCADE,
        related_name='test_cases',
        verbose_name=_('所属任务')
    )
    
    # Test case info
    module = models.CharField(_('模块'), max_length=100, blank=True)
    priority = models.CharField(
        _('优先级'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    # Execution info
    script_path = models.CharField(_('脚本路径'), max_length=500, blank=True)
    class_name = models.CharField(_('类名'), max_length=200, blank=True)
    method_name = models.CharField(_('方法名'), max_length=200, blank=True)
    parameters = models.JSONField(_('参数'), default=dict, blank=True)
    
    # Expected results
    expected_result = models.TextField(_('预期结果'), blank=True)
    preconditions = models.TextField(_('前置条件'), blank=True)
    
    # Status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    # ALM integration
    alm_case_id = models.CharField(_('ALM用例ID'), max_length=100, blank=True)
    
    # Estimated execution time in seconds
    estimated_time = models.IntegerField(_('预计执行时间(秒)'), null=True, blank=True)
    
    # Order for execution
    execution_order = models.IntegerField(_('执行顺序'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_cases'
        verbose_name = _('测试用例')
        verbose_name_plural = _('测试用例')
        ordering = ['execution_order', 'created_at']
        unique_together = [['task', 'case_code']]
    
    def __str__(self):
        return f"{self.case_code}: {self.name}"


class TestCaseResult(models.Model):
    """Test case execution result model."""
    
    class Status(models.TextChoices):
        """Result status choices."""
        PENDING = 'pending', _('待执行')
        RUNNING = 'running', _('执行中')
        PASSED = 'passed', _('通过')
        FAILED = 'failed', _('失败')
        SKIPPED = 'skipped', _('跳过')
        BLOCKED = 'blocked', _('阻塞')
        ERROR = 'error', _('错误')
    
    # Execution relationship
    execution = models.ForeignKey(
        'tasks.TaskExecution',
        on_delete=models.CASCADE,
        related_name='case_results',
        verbose_name=_('执行记录')
    )
    
    # Test case relationship
    test_case = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name=_('测试用例')
    )
    
    # Result status
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Timing
    start_time = models.DateTimeField(_('开始时间'), null=True, blank=True)
    end_time = models.DateTimeField(_('结束时间'), null=True, blank=True)
    duration_ms = models.IntegerField(_('执行时长(毫秒)'), null=True, blank=True)
    
    # Result details
    actual_result = models.TextField(_('实际结果'), blank=True)
    error_message = models.TextField(_('错误信息'), blank=True)
    stack_trace = models.TextField(_('堆栈信息'), blank=True)
    
    # Artifacts
    screenshot_path = models.CharField(_('截图路径'), max_length=500, blank=True)
    log_path = models.CharField(_('日志路径'), max_length=500, blank=True)
    
    # Retry info
    retry_count = models.IntegerField(_('重试次数'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'test_case_results'
        verbose_name = _('用例执行结果')
        verbose_name_plural = _('用例执行结果')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.test_case.case_code}: {self.get_status_display()}"
