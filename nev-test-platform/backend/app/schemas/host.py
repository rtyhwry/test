"""Test host schemas for API validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress
from app.models.host import HostStatus, HostOS


class TestHostBase(BaseModel):
    """Base test host schema."""
    name: str = Field(..., min_length=1, max_length=100)
    hostname: str = Field(..., max_length=255)
    ip_address: str = Field(..., max_length=45)
    ssh_port: int = Field(default=22, ge=1, le=65535)
    ssh_username: str = Field(default="root", max_length=50)


class TestHostCreate(TestHostBase):
    """Schema for creating a test host."""
    ssh_password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    os_type: HostOS = HostOS.LINUX
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None
    disk_gb: Optional[float] = None
    workspace_path: str = "/home/test/workspace"
    tags: Optional[List[str]] = None
    description: Optional[str] = None


class TestHostUpdate(BaseModel):
    """Schema for updating a test host."""
    name: Optional[str] = Field(None, max_length=100)
    hostname: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    ssh_port: Optional[int] = Field(None, ge=1, le=65535)
    ssh_username: Optional[str] = Field(None, max_length=50)
    ssh_password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    os_type: Optional[HostOS] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None
    disk_gb: Optional[float] = None
    workspace_path: Optional[str] = None
    status: Optional[HostStatus] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None


class TestHostResponse(TestHostBase):
    """Schema for test host response."""
    id: int
    os_type: HostOS
    os_version: Optional[str]
    cpu_cores: Optional[int]
    memory_gb: Optional[float]
    disk_gb: Optional[float]
    status: HostStatus
    last_heartbeat: Optional[str]
    workspace_path: str
    tags: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
