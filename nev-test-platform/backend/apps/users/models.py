"""User models for authentication and authorization."""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for the platform."""
    
    class Role(models.TextChoices):
        """User role choices."""
        ADMIN = 'admin', _('管理员')
        MANAGER = 'manager', _('项目经理')
        ENGINEER = 'engineer', _('测试工程师')
        VIEWER = 'viewer', _('访客')
    
    email = models.EmailField(_('邮箱'), unique=True)
    role = models.CharField(
        _('角色'),
        max_length=20,
        choices=Role.choices,
        default=Role.ENGINEER
    )
    department = models.CharField(_('部门'), max_length=100, blank=True)
    phone = models.CharField(_('电话'), max_length=20, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager(self):
        """Check if user is manager or above."""
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]
