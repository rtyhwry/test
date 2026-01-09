"""Test report model for storing generated reports."""
from sqlalchemy import String, Integer, Text, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from .base import BaseModel


class ReportFormat(str, enum.Enum):
    """Report format enumeration."""
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


class TestReport(BaseModel):
    """Test report model for execution reports."""
    __tablename__ = "test_reports"
    
    # Execution relationship
    execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("task_executions.id"), nullable=False, unique=True
    )
    execution: Mapped["TaskExecution"] = relationship(
        "TaskExecution", back_populates="report"
    )
    
    # Report info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Statistics
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    skipped_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Pass rate
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Duration
    total_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # File paths
    html_report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pdf_report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    excel_report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    json_report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Environment info at report time
    environment_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    host_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    device_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    
    # Version info
    software_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    git_branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    git_commit: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    
    # ALM sync
    alm_synced: Mapped[bool] = mapped_column(default=False, nullable=False)
    alm_sync_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    def __repr__(self) -> str:
        return f"<TestReport(id={self.id}, execution_id={self.execution_id}, pass_rate={self.pass_rate})>"
