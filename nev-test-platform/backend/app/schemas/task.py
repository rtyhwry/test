"""Test task schemas for API validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.task import ScheduleType, TaskStatus, ExecutionStatus


class TestTaskBase(BaseModel):
    """Base test task schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TestTaskCreate(TestTaskBase):
    """Schema for creating a test task."""
    project_id: int
    environment_id: Optional[int] = None
    
    # Scheduling
    schedule_type: ScheduleType = ScheduleType.MANUAL
    scheduled_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    timezone: str = "Asia/Shanghai"
    
    # Upgrade configuration
    need_upgrade: bool = False
    artifact_id: Optional[int] = None
    
    # Git configuration
    git_repo_url: Optional[str] = None
    git_branch: str = "main"
    git_tag: Optional[str] = None
    test_script_path: Optional[str] = None
    test_command: Optional[str] = None
    
    # ALM integration
    alm_task_id: Optional[str] = None
    alm_test_set_id: Optional[str] = None
    
    # Execution configuration
    timeout_minutes: int = 60
    retry_count: int = 0
    retry_interval_seconds: int = 60
    priority: int = 5


class TestTaskUpdate(BaseModel):
    """Schema for updating a test task."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    environment_id: Optional[int] = None
    schedule_type: Optional[ScheduleType] = None
    scheduled_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    need_upgrade: Optional[bool] = None
    artifact_id: Optional[int] = None
    git_repo_url: Optional[str] = None
    git_branch: Optional[str] = None
    git_tag: Optional[str] = None
    test_script_path: Optional[str] = None
    test_command: Optional[str] = None
    timeout_minutes: Optional[int] = None
    retry_count: Optional[int] = None
    retry_interval_seconds: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[TaskStatus] = None
    is_enabled: Optional[bool] = None


class TestTaskResponse(TestTaskBase):
    """Schema for test task response."""
    id: int
    project_id: int
    environment_id: Optional[int]
    schedule_type: ScheduleType
    scheduled_time: Optional[datetime]
    cron_expression: Optional[str]
    timezone: str
    need_upgrade: bool
    artifact_id: Optional[int]
    git_repo_url: Optional[str]
    git_branch: str
    git_tag: Optional[str]
    test_script_path: Optional[str]
    test_command: Optional[str]
    alm_task_id: Optional[str]
    alm_test_set_id: Optional[str]
    timeout_minutes: int
    retry_count: int
    retry_interval_seconds: int
    priority: int
    status: TaskStatus
    is_enabled: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    # Statistics
    last_execution_time: Optional[datetime] = None
    last_execution_status: Optional[ExecutionStatus] = None
    total_executions: int = 0
    
    class Config:
        from_attributes = True


class ExecuteTaskRequest(BaseModel):
    """Schema for task execution request."""
    environment_id: Optional[int] = None  # Override default environment
    force_upgrade: bool = False  # Force upgrade even if same version
    triggered_by: str = "manual"


class TaskExecutionResponse(BaseModel):
    """Schema for task execution response."""
    id: int
    task_id: int
    environment_id: int
    execution_number: int
    status: ExecutionStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[int]
    triggered_by: str
    triggered_user_id: Optional[int]
    artifact_version: Optional[str]
    git_commit: Optional[str]
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    log_path: Optional[str]
    error_message: Optional[str]
    celery_task_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskExecutionLog(BaseModel):
    """Schema for task execution log."""
    execution_id: int
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR
    message: str
    stage: str  # PREPARING, UPGRADING, PULLING_CODE, RUNNING, etc.
