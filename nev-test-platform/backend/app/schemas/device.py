"""Test device schemas for API validation."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.device import DeviceType, DeviceStatus


class TestDeviceBase(BaseModel):
    """Base test device schema."""
    name: str = Field(..., min_length=1, max_length=100)
    device_type: DeviceType
    serial_number: str = Field(..., min_length=1, max_length=100)


class TestDeviceCreate(TestDeviceBase):
    """Schema for creating a test device."""
    hardware_version: Optional[str] = None
    software_version: Optional[str] = None
    firmware_version: Optional[str] = None
    connection_type: Optional[str] = None
    connection_params: Optional[dict] = None
    environment_id: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TestDeviceUpdate(BaseModel):
    """Schema for updating a test device."""
    name: Optional[str] = Field(None, max_length=100)
    device_type: Optional[DeviceType] = None
    hardware_version: Optional[str] = None
    software_version: Optional[str] = None
    firmware_version: Optional[str] = None
    connection_type: Optional[str] = None
    connection_params: Optional[dict] = None
    status: Optional[DeviceStatus] = None
    environment_id: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TestDeviceResponse(TestDeviceBase):
    """Schema for test device response."""
    id: int
    hardware_version: Optional[str]
    software_version: Optional[str]
    firmware_version: Optional[str]
    connection_type: Optional[str]
    connection_params: Optional[str]
    status: DeviceStatus
    environment_id: Optional[int]
    manufacturer: Optional[str]
    model: Optional[str]
    description: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeviceUpgradeRequest(BaseModel):
    """Schema for device upgrade request."""
    artifact_id: int
    force: bool = False
