"""Test case and result models."""
from sqlalchemy import String, Integer, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
import enum

from .base import BaseModel


class TestCaseStatus(str, enum.Enum):
    """Test case status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class TestCaseResultStatus(str, enum.Enum):
    """Test case result status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"
    ERROR = "error"


class TestCasePriority(str, enum.Enum):
    """Test case priority enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestCase(BaseModel):
    """Test case model for individual test cases."""
    __tablename__ = "test_cases"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Task relationship
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_tasks.id"), nullable=False
    )
    task: Mapped["TestTask"] = relationship("TestTask", back_populates="test_cases")
    
    # Test case info
    case_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    module: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    priority: Mapped[TestCasePriority] = mapped_column(
        SQLEnum(TestCasePriority), default=TestCasePriority.MEDIUM, nullable=False
    )
    
    # Execution info
    script_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    class_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    method_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    parameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    
    # Expected results
    expected_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preconditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[TestCaseStatus] = mapped_column(
        SQLEnum(TestCaseStatus), default=TestCaseStatus.ACTIVE, nullable=False
    )
    
    # ALM integration
    alm_case_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Estimated execution time in seconds
    estimated_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Order for execution
    execution_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    results: Mapped[list["TestCaseResult"]] = relationship(
        "TestCaseResult", back_populates="test_case", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<TestCase(id={self.id}, name={self.name}, code={self.case_code})>"


class TestCaseResult(BaseModel):
    """Test case execution result model."""
    __tablename__ = "test_case_results"
    
    # Execution relationship
    execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("task_executions.id"), nullable=False
    )
    execution: Mapped["TaskExecution"] = relationship(
        "TaskExecution", back_populates="case_results"
    )
    
    # Test case relationship
    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id"), nullable=False
    )
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="results")
    
    # Result status
    status: Mapped[TestCaseResultStatus] = mapped_column(
        SQLEnum(TestCaseResultStatus), default=TestCaseResultStatus.PENDING, nullable=False
    )
    
    # Timing
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Result details
    actual_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Artifacts
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    log_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Retry info
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    def __repr__(self) -> str:
        return f"<TestCaseResult(id={self.id}, case_id={self.test_case_id}, status={self.status})>"
