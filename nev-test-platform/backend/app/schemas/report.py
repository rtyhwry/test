"""Test report schemas for API validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.report import ReportFormat


class TestReportResponse(BaseModel):
    """Schema for test report response."""
    id: int
    execution_id: int
    title: str
    summary: Optional[str]
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    blocked_cases: int
    error_cases: int
    pass_rate: float
    total_duration_seconds: Optional[int]
    html_report_path: Optional[str]
    pdf_report_path: Optional[str]
    excel_report_path: Optional[str]
    json_report_path: Optional[str]
    environment_name: Optional[str]
    host_info: Optional[str]
    device_info: Optional[str]
    software_version: Optional[str]
    git_branch: Optional[str]
    git_commit: Optional[str]
    alm_synced: bool
    alm_sync_time: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    """Schema for report generation request."""
    formats: List[ReportFormat] = [ReportFormat.HTML]
    include_logs: bool = True
    include_screenshots: bool = True


class ReportStatistics(BaseModel):
    """Schema for report statistics."""
    total_executions: int
    total_cases_executed: int
    total_passed: int
    total_failed: int
    average_pass_rate: float
    average_duration_seconds: float
    
    # Trend data
    daily_stats: Optional[List[dict]] = None
    weekly_stats: Optional[List[dict]] = None


class ReportSubscription(BaseModel):
    """Schema for report subscription."""
    email: str
    task_ids: List[int]
    frequency: str  # "always", "daily", "weekly", "on_failure"
    formats: List[ReportFormat] = [ReportFormat.HTML]
