"""Test environment schemas for API validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.environment import EnvironmentStatus
from .host import TestHostResponse
from .device import TestDeviceResponse


class TestEnvironmentBase(BaseModel):
    """Base test environment schema."""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)


class TestEnvironmentCreate(TestEnvironmentBase):
    """Schema for creating a test environment."""
    project_id: int
    host_id: int
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_auto_release: bool = True
    max_lock_hours: int = 24


class TestEnvironmentUpdate(BaseModel):
    """Schema for updating a test environment."""
    name: Optional[str] = Field(None, max_length=100)
    host_id: Optional[int] = None
    status: Optional[EnvironmentStatus] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_auto_release: Optional[bool] = None
    max_lock_hours: Optional[int] = None


class TestEnvironmentResponse(TestEnvironmentBase):
    """Schema for test environment response."""
    id: int
    project_id: int
    host_id: int
    status: EnvironmentStatus
    locked_by: Optional[int]
    locked_at: Optional[str]
    lock_reason: Optional[str]
    is_auto_release: bool
    max_lock_hours: int
    description: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    host: Optional[TestHostResponse] = None
    devices: Optional[List[TestDeviceResponse]] = None
    
    class Config:
        from_attributes = True


class EnvironmentLockRequest(BaseModel):
    """Schema for environment lock request."""
    reason: Optional[str] = None
    duration_hours: Optional[int] = None
