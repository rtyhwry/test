"""Test task and execution models."""
from sqlalchemy import String, Integer, Text, ForeignKey, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
import enum

from .base import BaseModel


class ScheduleType(str, enum.Enum):
    """Task schedule type enumeration."""
    IMMEDIATE = "immediate"  # Execute immediately
    SCHEDULED = "scheduled"  # Execute at scheduled time
    CRON = "cron"  # Execute on cron schedule
    MANUAL = "manual"  # Manual trigger only


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionStatus(str, enum.Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    PREPARING = "preparing"  # Setting up environment
    UPGRADING = "upgrading"  # Upgrading device
    PULLING_CODE = "pulling_code"  # Pulling test code
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TestTask(BaseModel):
    """Test task model for scheduling and managing test executions."""
    __tablename__ = "test_tasks"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Project relationship
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    
    # Environment relationship
    environment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("test_environments.id"), nullable=True
    )
    environment: Mapped[Optional["TestEnvironment"]] = relationship(
        "TestEnvironment", back_populates="tasks"
    )
    
    # Scheduling
    schedule_type: Mapped[ScheduleType] = mapped_column(
        SQLEnum(ScheduleType), default=ScheduleType.MANUAL, nullable=False
    )
    scheduled_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Shanghai", nullable=False)
    
    # Upgrade configuration
    need_upgrade: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    artifact_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("artifacts.id"), nullable=True
    )
    
    # Git configuration
    git_repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    git_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    git_tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    test_script_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    test_command: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ALM integration
    alm_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    alm_test_set_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Execution configuration
    timeout_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_interval_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    # Priority (higher = more important)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # Status
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.DRAFT, nullable=False
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Creator
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_tasks", foreign_keys=[created_by]
    )
    
    # Relationships
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase", back_populates="task", cascade="all, delete-orphan"
    )
    executions: Mapped[List["TaskExecution"]] = relationship(
        "TaskExecution", back_populates="task", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<TestTask(id={self.id}, name={self.name}, status={self.status})>"


class TaskExecution(BaseModel):
    """Task execution record model."""
    __tablename__ = "task_executions"
    
    # Task relationship
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_tasks.id"), nullable=False
    )
    task: Mapped["TestTask"] = relationship("TestTask", back_populates="executions")
    
    # Environment relationship
    environment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_environments.id"), nullable=False
    )
    environment: Mapped["TestEnvironment"] = relationship(
        "TestEnvironment", back_populates="executions"
    )
    
    # Execution info
    execution_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False
    )
    
    # Timing
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Trigger info
    triggered_by: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)  # manual, scheduled, api
    triggered_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # Version info at execution time
    artifact_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    git_commit: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    
    # Results
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Logs and artifacts
    log_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Celery task info
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    case_results: Mapped[List["TestCaseResult"]] = relationship(
        "TestCaseResult", back_populates="execution", cascade="all, delete-orphan"
    )
    report: Mapped[Optional["TestReport"]] = relationship(
        "TestReport", back_populates="execution", uselist=False
    )
    
    def __repr__(self) -> str:
        return f"<TaskExecution(id={self.id}, task_id={self.task_id}, status={self.status})>"
