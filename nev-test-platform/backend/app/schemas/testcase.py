"""Test case schemas for API validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.testcase import TestCaseStatus, TestCaseResultStatus, TestCasePriority


class TestCaseBase(BaseModel):
    """Base test case schema."""
    name: str = Field(..., min_length=1, max_length=200)
    case_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class TestCaseCreate(TestCaseBase):
    """Schema for creating a test case."""
    task_id: int
    module: Optional[str] = None
    priority: TestCasePriority = TestCasePriority.MEDIUM
    script_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    parameters: Optional[dict] = None
    expected_result: Optional[str] = None
    preconditions: Optional[str] = None
    alm_case_id: Optional[str] = None
    estimated_time: Optional[int] = None
    execution_order: int = 0


class TestCaseUpdate(BaseModel):
    """Schema for updating a test case."""
    name: Optional[str] = Field(None, max_length=200)
    case_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    module: Optional[str] = None
    priority: Optional[TestCasePriority] = None
    script_path: Optional[str] = None
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    parameters: Optional[dict] = None
    expected_result: Optional[str] = None
    preconditions: Optional[str] = None
    status: Optional[TestCaseStatus] = None
    estimated_time: Optional[int] = None
    execution_order: Optional[int] = None


class TestCaseResponse(TestCaseBase):
    """Schema for test case response."""
    id: int
    task_id: int
    module: Optional[str]
    priority: TestCasePriority
    script_path: Optional[str]
    class_name: Optional[str]
    method_name: Optional[str]
    parameters: Optional[str]
    expected_result: Optional[str]
    preconditions: Optional[str]
    status: TestCaseStatus
    alm_case_id: Optional[str]
    estimated_time: Optional[int]
    execution_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestCaseResultResponse(BaseModel):
    """Schema for test case result response."""
    id: int
    execution_id: int
    test_case_id: int
    status: TestCaseResultStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    actual_result: Optional[str]
    error_message: Optional[str]
    stack_trace: Optional[str]
    screenshot_path: Optional[str]
    log_path: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    # Related test case info
    test_case: Optional[TestCaseResponse] = None
    
    class Config:
        from_attributes = True


class TestCaseBatchCreate(BaseModel):
    """Schema for batch creating test cases."""
    task_id: int
    cases: List[TestCaseCreate]
