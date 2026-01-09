"""Artifact schemas for API validation."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.artifact import ArtifactType


class ArtifactBase(BaseModel):
    """Base artifact schema."""
    name: str = Field(..., min_length=1, max_length=200)
    version: str = Field(..., min_length=1, max_length=50)
    artifact_type: ArtifactType


class ArtifactCreate(ArtifactBase):
    """Schema for creating an artifact."""
    repository: str
    group_id: Optional[str] = None
    artifact_id: str
    file_name: str
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    download_url: str
    target_device_type: Optional[str] = None
    description: Optional[str] = None
    release_notes: Optional[str] = None
    build_number: Optional[str] = None
    branch: Optional[str] = None
    commit_hash: Optional[str] = None


class ArtifactResponse(ArtifactBase):
    """Schema for artifact response."""
    id: int
    repository: str
    group_id: Optional[str]
    artifact_id: str
    file_name: str
    file_size: Optional[int]
    checksum: Optional[str]
    download_url: str
    target_device_type: Optional[str]
    description: Optional[str]
    release_notes: Optional[str]
    build_number: Optional[str]
    branch: Optional[str]
    commit_hash: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArtifactSyncRequest(BaseModel):
    """Schema for syncing artifacts from repository."""
    repository: str
    group_id: Optional[str] = None
    artifact_id: Optional[str] = None
    version_pattern: Optional[str] = None  # Regex pattern for versions
